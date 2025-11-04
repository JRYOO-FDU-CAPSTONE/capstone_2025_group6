# Save as: capstone_2025_group6/BCacheSim/cachesim/a5_eviction_policies.py

from .eviction_policies import EvictionPolicy
from collections import OrderedDict

class EDE(EvictionPolicy):
    """
    Episode-Deadline Eviction (EDE, E2)
    
    Implementation based on A4.docx and A5.docx requirements.
    
    This policy maintains two segments: Probation and Protected.
    - 'protected_cap' controls the size of the protected segment.
    - 'otti' (alpha) controls the EWMA for time-to-idle (TTI) estimates.
    
    Logic:
    1. New items are admitted to the 'probation' segment.
    2. A hit in 'probation' promotes the item to 'protected'.
    3. A hit in 'protected' refreshes its position (LRU).
    4. If 'protected' exceeds its 'protected_cap', the LRU item
       from 'protected' is demoted to 'probation'.
    5. Victim selection always comes from 'probation' first.
    6. The victim chosen from 'probation' is the one with the
       *closest predicted deadline* (smallest TTI estimate).
    7. If 'probation' is empty, the victim is the LRU from 'protected'.
    """
    def __init__(self, cache_size, protected_cap: float = 0.5, otti: float = 0.5):
        self.cache_size = cache_size
        self.protected_cap_ratio = protected_cap
        self.otti = otti  # This is the 'alpha' for the EWMA
        
        self.protected_size_limit = self.cache_size * self.protected_cap_ratio
        
        # Data structures for the two segments
        self.protected_lru = OrderedDict()
        self.probation_lru = OrderedDict() # This will be managed by deadline
        
        self.current_protected_size = 0
        self.current_probation_size = 0
        
        # Data structures for TTI and deadline prediction
        self.tti_estimates = {}  # Stores the EWMA TTI for each key
        self.deadlines = {}      # Stores the predicted expiry timestamp
        self.last_access_time = {} # Stores the last access timestamp for TTI calc

    def on_admit(self, key, size, metadata):
        """Called when an item is admitted to the cache."""
        ts = metadata['timestamp']
        
        # New items are added to the probation segment
        self.probation_lru[key] = {'size': size, **metadata}
        self.current_probation_size += size
        
        # Store its last access time
        self.last_access_time[key] = ts
        
        # Give it an infinite deadline until its first re-hit
        self.deadlines[key] = float('inf')

    def on_evict(self, key):
        """Called when an item is evicted (after choose_victim)."""
        
        # Remove from whichever segment it's in
        if key in self.protected_lru:
            size = self.protected_lru.pop(key)['size']
            self.current_protected_size -= size
        elif key in self.probation_lru:
            size = self.probation_lru.pop(key)['size']
            self.current_probation_size -= size
            
        # Clean up tracking metadata
        self.tti_estimates.pop(key, None)
        self.deadlines.pop(key, None)
        self.last_access_time.pop(key, None)

    def on_hit(self, key, size, metadata):
        """Called on a cache hit. This is where TTI is updated."""
        ts = metadata['timestamp']
        
        # --- 1. Update TTI and Deadline ---
        if key in self.last_access_time:
            # Calculate observed TTI (time since last access)
            observed_tti = ts - self.last_access_time[key]
            
            # Get old estimate, or use first observation
            old_tti_estimate = self.tti_estimates.get(key, observed_tti)
            
            # Calculate new EWMA TTI estimate
            alpha = self.otti
            new_tti_estimate = (alpha * observed_tti) + ((1 - alpha) * old_tti_estimate)
            
            # Store new estimate and predicted deadline
            self.tti_estimates[key] = new_tti_estimate
            self.deadlines[key] = ts + new_tti_estimate
        
        # Update the last access time
        self.last_access_time[key] = ts

        # --- 2. Handle Promotion / Refresh ---
        if key in self.probation_lru:
            # --- Promotion: Probation -> Protected ---
            item = self.probation_lru.pop(key)
            self.current_probation_size -= size
            
            self.protected_lru[key] = item
            self.current_protected_size += size
            self.protected_lru.move_to_end(key) # Move to MRU
            
        elif key in self.protected_lru:
            # --- Refresh: Move to MRU in Protected ---
            self.protected_lru.move_to_end(key)
            
        # --- 3. Handle Demotion (Protected Overflow) ---
        while self.current_protected_size > self.protected_size_limit:
            # Pop LRU item from protected
            demoted_key, demoted_item = self.protected_lru.popitem(last=False)
            self.current_protected_size -= demoted_item['size']
            
            # Add to probation
            self.probation_lru[demoted_key] = demoted_item
            self.current_probation_size += demoted_item['size']

    def on_miss(self, key, size, metadata):
        pass

    def choose_victim(self):
        """Called by the cache to select an item for eviction."""
        
        # Rule 1: Always evict from probation segment if it has items.
        if self.current_probation_size > 0:
            
            # --- EDE Logic: Evict item with closest deadline ---
            # Find the key in probation_lru with the minimum deadline
            victim_key = min(
                self.probation_lru.keys(), 
                key=lambda k: self.deadlines.get(k, float('inf'))
            )
            return victim_key
            
        # Rule 2: If probation is empty, evict LRU from protected.
        elif self.current_protected_size > 0:
            victim_key, _ = self.protected_lru.popitem(last=False)
            return victim_key
            
        # Cache is empty
        return None