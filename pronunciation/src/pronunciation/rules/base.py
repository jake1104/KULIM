from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Phoneme:
    code: str  # Original character (e.g., '가') or decomposed part
    cho: str
    jung: str
    jong: str
    
    # Metadata for rule application
    is_hangul: bool = True
    original_jong: str = "" # To track underlying form before neutralization
    
    # Linked list structure for easy context access
    prev: Optional['Phoneme'] = None
    next: Optional['Phoneme'] = None

    def compose(self):
        """Re-compose into Hangul char if valid."""
        # Use simple import inside method to avoid circular dependency if needed
        # But here we expect hangul module availability
        from hangul import compose
        if not self.is_hangul:
            return self.code
        return compose(self.cho, self.jung, self.jong)

class PronunciationRule(ABC):
    """Abstract Base Class for Phonological Rules."""
    
    @abstractmethod
    def apply(self, phonemes: List[Phoneme]) -> List[Phoneme]:
        """Apply the rule to the sequence of phonemes.
        
        Args:
            phonemes: List of Phoneme objects representing the text.
            
        Returns:
            Modified list of phonemes (in-place modification is allowed and preferred).
        """
        pass
