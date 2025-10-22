"""
Grammar and writing analysis tools
"""
import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class GrammarChecker:
    def __init__(self):
        # Basic grammar rules (expandable)
        self.common_errors = {
            'its_vs_its': {
                'pattern': r'\bits\s+(?:a|an|the|very|really|quite)',
                'suggestion': "Consider using \"it's\" (it is) instead of \"its\""
            },
            'there_their_theyre': {
                'pattern': r'\btheir\s+(?:is|are|was|were)',
                'suggestion': "Consider using \"there\" instead of \"their\""
            },
            'your_youre': {
                'pattern': r'\byour\s+(?:a|an|the|very|really|quite|going|coming)',
                'suggestion': "Consider using \"you're\" (you are) instead of \"your\""
            },
            'double_spaces': {
                'pattern': r'\s{2,}',
                'suggestion': "Remove extra spaces"
            },
            'comma_splice': {
                'pattern': r'[a-z]+,\s*[A-Z][a-z]+',
                'suggestion': "Possible comma splice - consider using semicolon or period"
            }
        }
        
        # Readability metrics
        self.readability_weights = {
            'avg_sentence_length': 0.3,
            'syllable_complexity': 0.2,
            'word_frequency': 0.2,
            'sentence_variety': 0.3
        }
    
    def check_grammar(self, text):
        """Basic grammar checking"""
        issues = []
        
        for error_type, rule in self.common_errors.items():
            matches = list(re.finditer(rule['pattern'], text, re.IGNORECASE))
            for match in matches:
                issues.append({
                    'type': error_type,
                    'position': match.start(),
                    'text': match.group(),
                    'suggestion': rule['suggestion'],
                    'severity': 'medium'
                })
        
        return issues
    
    def analyze_readability(self, text):
        """Calculate readability metrics"""
        try:
            sentences = self._split_sentences(text)
            words = self._split_words(text)
            
            if not sentences or not words:
                return {'error': 'Text too short for analysis'}
            
            # Basic metrics
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Syllable estimation (rough)
            syllables = sum(self._count_syllables(word) for word in words)
            avg_syllables_per_word = syllables / len(words)
            
            # Flesch Reading Ease (simplified)
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            flesch_score = max(0, min(100, flesch_score))
            
            # Grade level estimation
            grade_level = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
            grade_level = max(1, min(20, grade_level))
            
            return {
                'flesch_reading_ease': round(flesch_score, 1),
                'grade_level': round(grade_level, 1),
                'avg_sentence_length': round(avg_sentence_length, 1),
                'avg_word_length': round(avg_word_length, 1),
                'total_sentences': len(sentences),
                'total_words': len(words),
                'total_syllables': syllables,
                'readability_level': self._get_readability_level(flesch_score)
            }
            
        except Exception as e:
            logger.error(f"Readability analysis error: {e}")
            return {'error': str(e)}
    
    def analyze_writing_style(self, text):
        """Analyze writing style and patterns"""
        try:
            sentences = self._split_sentences(text)
            words = self._split_words(text)
            
            # Sentence length variety
            sentence_lengths = [len(self._split_words(s)) for s in sentences]
            length_variety = len(set(sentence_lengths)) / len(sentence_lengths) if sentence_lengths else 0
            
            # Word frequency analysis
            word_freq = Counter(word.lower() for word in words if len(word) > 3)
            most_common = word_freq.most_common(5)
            
            # Passive voice detection (basic)
            passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
            passive_count = sum(1 for word in words if word.lower() in passive_indicators)
            passive_ratio = passive_count / len(words) if words else 0
            
            # Transition words
            transitions = ['however', 'therefore', 'furthermore', 'moreover', 'consequently']
            transition_count = sum(1 for word in words if word.lower() in transitions)
            
            return {
                'sentence_variety': round(length_variety, 2),
                'most_common_words': most_common,
                'passive_voice_ratio': round(passive_ratio, 3),
                'transition_word_count': transition_count,
                'avg_sentence_length': round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0,
                'vocabulary_richness': round(len(set(words)) / len(words), 3) if words else 0
            }
            
        except Exception as e:
            logger.error(f"Writing style analysis error: {e}")
            return {'error': str(e)}
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_words(self, text):
        """Split text into words"""
        words = re.findall(r'\b\w+\b', text)
        return [w for w in words if len(w) > 0]
    
    def _count_syllables(self, word):
        """Estimate syllable count (basic algorithm)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _get_readability_level(self, flesch_score):
        """Convert Flesch score to readability level"""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

# Global grammar checker instance
grammar_checker = GrammarChecker()