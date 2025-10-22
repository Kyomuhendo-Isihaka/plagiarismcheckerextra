import re
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Citation:
    id: str
    type: str  # 'book', 'journal', 'website', 'conference'
    authors: List[str]
    title: str
    year: int
    publisher: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None

class CitationManager:
    def __init__(self):
        self.citations = {}
        self.citation_styles = {
            'APA': self._format_apa,
            'MLA': self._format_mla,
            'Chicago': self._format_chicago,
            'IEEE': self._format_ieee
        }
    
    def analyze_document_citations(self, text):
        """Analyze citations in document and extract references"""
        results = {
            'detected_citations': self._detect_citations(text),
            'missing_citations': self._find_missing_citations(text),
            'citation_quality': self._assess_citation_quality(text),
            'suggestions': self._generate_suggestions(text),
            'bibliography': self._extract_bibliography(text)
        }
        
        return results
    
    def _detect_citations(self, text):
        """Detect various citation formats in text"""
        citations = {
            'in_text': [],
            'parenthetical': [],
            'numbered': [],
            'footnotes': []
        }
        
        # APA/MLA style: (Author, Year) or (Author Year)
        apa_pattern = r'\(([A-Za-z\s&,]+),?\s*(\d{4})[a-z]?\)'
        apa_matches = re.finditer(apa_pattern, text)
        for match in apa_matches:
            citations['parenthetical'].append({
                'text': match.group(0),
                'author': match.group(1).strip(),
                'year': match.group(2),
                'position': match.span(),
                'style': 'APA/MLA'
            })
        
        # Numbered citations: [1], [2], etc.
        numbered_pattern = r'\[(\d+)\]'
        numbered_matches = re.finditer(numbered_pattern, text)
        for match in numbered_matches:
            citations['numbered'].append({
                'text': match.group(0),
                'number': match.group(1),
                'position': match.span(),
                'style': 'IEEE/Numbered'
            })
        
        # Author-year in text: "Smith (2023) argues..."
        author_year_pattern = r'([A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+)*)\s*\((\d{4})[a-z]?\)'
        author_matches = re.finditer(author_year_pattern, text)
        for match in author_matches:
            citations['in_text'].append({
                'text': match.group(0),
                'author': match.group(1),
                'year': match.group(2),
                'position': match.span(),
                'style': 'Author-Year'
            })
        
        return citations
    
    def _find_missing_citations(self, text):
        """Find statements that likely need citations"""
        missing_citations = []
        
        # Patterns that typically need citations
        citation_needed_patterns = [
            r'studies show that',
            r'research indicates',
            r'according to',
            r'statistics reveal',
            r'data suggests',
            r'experts believe',
            r'it has been proven',
            r'evidence suggests'
        ]
        
        sentences = text.split('.')
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            for pattern in citation_needed_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    # Check if sentence already has citation
                    has_citation = (
                        re.search(r'\([A-Za-z\s&,]+,?\s*\d{4}\)', sentence) or
                        re.search(r'\[\d+\]', sentence) or
                        re.search(r'[A-Z][a-z]+\s*\(\d{4}\)', sentence)
                    )
                    
                    if not has_citation:
                        missing_citations.append({
                            'sentence': sentence,
                            'sentence_number': i + 1,
                            'reason': f'Contains "{pattern}" without citation',
                            'severity': 'High'
                        })
        
        return missing_citations
    
    def _assess_citation_quality(self, text):
        """Assess overall citation quality"""
        detected = self._detect_citations(text)
        total_citations = sum(len(citations) for citations in detected.values())
        
        word_count = len(text.split())
        citation_density = total_citations / max(word_count / 100, 1)  # Citations per 100 words
        
        # Check for citation consistency
        styles_used = set()
        for citation_type in detected.values():
            for citation in citation_type:
                styles_used.add(citation.get('style', 'Unknown'))
        
        consistency_score = 1.0 if len(styles_used) <= 1 else 0.5
        
        quality_score = min((citation_density / 2) + consistency_score, 2.0) / 2.0
        
        return {
            'total_citations': total_citations,
            'citation_density': citation_density,
            'styles_used': list(styles_used),
            'consistency_score': consistency_score,
            'overall_quality': quality_score,
            'grade': self._get_quality_grade(quality_score)
        }
    
    def _generate_suggestions(self, text):
        """Generate citation improvement suggestions"""
        suggestions = []
        
        detected = self._detect_citations(text)
        missing = self._find_missing_citations(text)
        quality = self._assess_citation_quality(text)
        
        # Density suggestions
        if quality['citation_density'] < 1.0:
            suggestions.append({
                'type': 'Density',
                'message': 'Consider adding more citations to support your arguments',
                'priority': 'Medium'
            })
        
        # Consistency suggestions
        if len(quality['styles_used']) > 1:
            suggestions.append({
                'type': 'Consistency',
                'message': f'Multiple citation styles detected: {", ".join(quality["styles_used"])}. Use consistent style throughout.',
                'priority': 'High'
            })
        
        # Missing citation suggestions
        if len(missing) > 0:
            suggestions.append({
                'type': 'Missing Citations',
                'message': f'{len(missing)} statements found that likely need citations',
                'priority': 'High'
            })
        
        # Format suggestions
        for citation_type, citations in detected.items():
            for citation in citations:
                if not self._validate_citation_format(citation):
                    suggestions.append({
                        'type': 'Format',
                        'message': f'Citation "{citation["text"]}" may have formatting issues',
                        'priority': 'Medium'
                    })
        
        return suggestions
    
    def _extract_bibliography(self, text):
        """Extract bibliography/references section"""
        # Look for common bibliography section headers
        bib_patterns = [
            r'(?i)(references|bibliography|works cited|sources)\s*\n',
            r'(?i)(references|bibliography|works cited|sources)\s*:',
        ]
        
        bibliography_start = None
        for pattern in bib_patterns:
            match = re.search(pattern, text)
            if match:
                bibliography_start = match.end()
                break
        
        if not bibliography_start:
            return {'found': False, 'entries': []}
        
        # Extract bibliography section
        bib_text = text[bibliography_start:]
        
        # Parse individual entries (simple approach)
        entries = []
        lines = bib_text.split('\n')
        
        current_entry = ""
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    entries.append(self._parse_bibliography_entry(current_entry))
                    current_entry = ""
            else:
                current_entry += " " + line if current_entry else line
        
        if current_entry:
            entries.append(self._parse_bibliography_entry(current_entry))
        
        return {
            'found': True,
            'entries': entries,
            'total_count': len(entries)
        }
    
    def _parse_bibliography_entry(self, entry):
        """Parse a single bibliography entry"""
        # Simple parsing - extract basic information
        parsed = {
            'raw_text': entry,
            'authors': [],
            'title': '',
            'year': None,
            'type': 'unknown'
        }
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', entry)
        if year_match:
            parsed['year'] = int(year_match.group())
        
        # Extract potential title (text in quotes or italics)
        title_match = re.search(r'["\']([^"\']+)["\']', entry)
        if not title_match:
            title_match = re.search(r'\*([^*]+)\*', entry)
        if title_match:
            parsed['title'] = title_match.group(1)
        
        # Extract authors (names before year or title)
        author_pattern = r'^([A-Z][a-z]+(?:,\s*[A-Z]\.)*(?:\s*&\s*[A-Z][a-z]+(?:,\s*[A-Z]\.)*)*)'
        author_match = re.search(author_pattern, entry)
        if author_match:
            parsed['authors'] = [author_match.group(1)]
        
        return parsed
    
    def _validate_citation_format(self, citation):
        """Validate citation format"""
        # Basic validation - check for common issues
        text = citation.get('text', '')
        
        # Check for proper parentheses
        if text.count('(') != text.count(')'):
            return False
        
        # Check for year format
        if citation.get('year'):
            year = int(citation['year'])
            if year < 1900 or year > datetime.now().year + 1:
                return False
        
        return True
    
    def _get_quality_grade(self, score):
        """Convert quality score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def format_citation(self, citation: Citation, style: str = 'APA'):
        """Format citation in specified style"""
        formatter = self.citation_styles.get(style, self._format_apa)
        return formatter(citation)
    
    def _format_apa(self, citation: Citation):
        """Format citation in APA style"""
        authors = self._format_authors_apa(citation.authors)
        
        if citation.type == 'journal':
            return f"{authors} ({citation.year}). {citation.title}. *{citation.journal}*, {citation.volume}, {citation.pages}."
        elif citation.type == 'book':
            return f"{authors} ({citation.year}). *{citation.title}*. {citation.publisher}."
        elif citation.type == 'website':
            return f"{authors} ({citation.year}). {citation.title}. Retrieved from {citation.url}"
        else:
            return f"{authors} ({citation.year}). {citation.title}."
    
    def _format_mla(self, citation: Citation):
        """Format citation in MLA style"""
        authors = self._format_authors_mla(citation.authors)
        
        if citation.type == 'journal':
            return f'{authors} "{citation.title}." *{citation.journal}*, vol. {citation.volume}, {citation.year}, pp. {citation.pages}.'
        elif citation.type == 'book':
            return f'{authors} *{citation.title}*. {citation.publisher}, {citation.year}.'
        else:
            return f'{authors} "{citation.title}." {citation.year}.'
    
    def _format_chicago(self, citation: Citation):
        """Format citation in Chicago style"""
        authors = self._format_authors_chicago(citation.authors)
        
        if citation.type == 'journal':
            return f'{authors} "{citation.title}." {citation.journal} {citation.volume} ({citation.year}): {citation.pages}.'
        elif citation.type == 'book':
            return f'{authors} *{citation.title}*. {citation.publisher}, {citation.year}.'
        else:
            return f'{authors} "{citation.title}." {citation.year}.'
    
    def _format_ieee(self, citation: Citation):
        """Format citation in IEEE style"""
        authors = self._format_authors_ieee(citation.authors)
        
        if citation.type == 'journal':
            return f'{authors} "{citation.title}," *{citation.journal}*, vol. {citation.volume}, pp. {citation.pages}, {citation.year}.'
        elif citation.type == 'book':
            return f'{authors} *{citation.title}*. {citation.publisher}, {citation.year}.'
        else:
            return f'{authors} "{citation.title}," {citation.year}.'
    
    def _format_authors_apa(self, authors):
        """Format authors for APA style"""
        if not authors:
            return ""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_authors_mla(self, authors):
        """Format authors for MLA style"""
        if not authors:
            return ""
        return authors[0]  # MLA uses first author only for in-text
    
    def _format_authors_chicago(self, authors):
        """Format authors for Chicago style"""
        if not authors:
            return ""
        return authors[0]  # Simplified
    
    def _format_authors_ieee(self, authors):
        """Format authors for IEEE style"""
        if not authors:
            return ""
        if len(authors) == 1:
            return authors[0]
        else:
            return f"{authors[0]} et al."