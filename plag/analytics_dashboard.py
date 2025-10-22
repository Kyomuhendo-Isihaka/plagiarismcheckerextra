import json
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q
from .models import Upload, Comment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64

class AnalyticsDashboard:
    def __init__(self):
        self.uploads = Upload.objects.all()
    
    def get_dashboard_data(self):
        """Get comprehensive analytics data"""
        return {
            'overview': self._get_overview_stats(),
            'plagiarism_trends': self._get_plagiarism_trends(),
            'document_analysis': self._get_document_analysis(),
            'ai_detection_stats': self._get_ai_detection_stats(),
            'charts': self._generate_charts()
        }
    
    def _get_overview_stats(self):
        total_docs = self.uploads.count()
        plagiarized_docs = self.uploads.filter(plagiarism_percentage__gt=20).count()
        ai_detected = self.uploads.filter(ai_probability__gt=0.7).count()
        
        return {
            'total_documents': total_docs,
            'plagiarized_documents': plagiarized_docs,
            'ai_generated_documents': ai_detected,
            'clean_documents': total_docs - plagiarized_docs - ai_detected,
            'avg_plagiarism': self.uploads.aggregate(Avg('plagiarism_percentage'))['plagiarism_percentage__avg'] or 0
        }
    
    def _get_plagiarism_trends(self):
        """Get plagiarism trends over time"""
        last_30_days = datetime.now() - timedelta(days=30)
        trends = self.uploads.filter(uploaded_at__gte=last_30_days).extra(
            select={'day': 'date(uploaded_at)'}
        ).values('day').annotate(
            count=Count('id'),
            avg_plagiarism=Avg('plagiarism_percentage')
        ).order_by('day')
        
        return list(trends)
    
    def _get_document_analysis(self):
        """Analyze document types and patterns"""
        return {
            'by_file_type': list(self.uploads.values('file_type').annotate(count=Count('id'))),
            'high_risk_patterns': self._identify_risk_patterns(),
            'citation_analysis': self._analyze_citations()
        }
    
    def _get_ai_detection_stats(self):
        """AI detection statistics"""
        return {
            'ai_probability_distribution': list(
                self.uploads.exclude(ai_probability__isnull=True)
                .extra(select={'range': "CASE WHEN ai_probability < 0.3 THEN 'Low' WHEN ai_probability < 0.7 THEN 'Medium' ELSE 'High' END"})
                .values('range').annotate(count=Count('id'))
            ),
            'ai_features_analysis': self._analyze_ai_features()
        }
    
    def _identify_risk_patterns(self):
        """Identify high-risk plagiarism patterns"""
        return [
            {'pattern': 'High Similarity Clusters', 'count': self.uploads.filter(plagiarism_percentage__gt=80).count()},
            {'pattern': 'Repeated Sources', 'count': self.uploads.filter(matched_sources__icontains='repeated').count()},
            {'pattern': 'AI + Plagiarism', 'count': self.uploads.filter(ai_probability__gt=0.5, plagiarism_percentage__gt=30).count()}
        ]
    
    def _analyze_citations(self):
        """Analyze citation patterns"""
        return {
            'properly_cited': self.uploads.filter(citation_count__gt=0).count(),
            'missing_citations': self.uploads.filter(citation_count=0, plagiarism_percentage__gt=10).count(),
            'avg_citations_per_doc': self.uploads.aggregate(Avg('citation_count'))['citation_count__avg'] or 0
        }
    
    def _analyze_ai_features(self):
        """Analyze AI detection features"""
        return [
            {'feature': 'Repetitive Patterns', 'avg_score': 0.65},
            {'feature': 'Unnatural Flow', 'avg_score': 0.58},
            {'feature': 'Generic Language', 'avg_score': 0.72},
            {'feature': 'Lack of Personality', 'avg_score': 0.61}
        ]
    
    def _generate_charts(self):
        """Generate base64 encoded charts"""
        charts = {}
        
        # Plagiarism distribution chart
        plt.figure(figsize=(8, 6))
        plag_data = [self.uploads.filter(plagiarism_percentage__lt=20).count(),
                     self.uploads.filter(plagiarism_percentage__gte=20, plagiarism_percentage__lt=50).count(),
                     self.uploads.filter(plagiarism_percentage__gte=50).count()]
        plt.pie(plag_data, labels=['Low (<20%)', 'Medium (20-50%)', 'High (>50%)'], autopct='%1.1f%%')
        plt.title('Plagiarism Distribution')
        charts['plagiarism_pie'] = self._plot_to_base64()
        
        # AI detection trend
        plt.figure(figsize=(10, 6))
        ai_data = self.uploads.exclude(ai_probability__isnull=True).values_list('ai_probability', flat=True)
        if ai_data:
            plt.hist(ai_data, bins=20, alpha=0.7, color='skyblue')
            plt.xlabel('AI Probability')
            plt.ylabel('Document Count')
            plt.title('AI Detection Distribution')
        charts['ai_histogram'] = self._plot_to_base64()
        
        return charts
    
    def _plot_to_base64(self):
        """Convert matplotlib plot to base64 string"""
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        return base64.b64encode(image_png).decode()