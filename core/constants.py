# core/constants.py

COMMON_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'such', 'which', 'what', 'who', 'when', 'where',
    'why', 'how', 'their', 'there', 'they', 'them', 'then', 'than',
    'your', 'you', 'we', 'our', 'us', 'it', 'its'
}

IMPACT_VERBS = [
    'achieved', 'improved', 'increased', 'decreased', 'developed',
    'created', 'led', 'managed', 'launched', 'implemented', 'delivered',
    'designed', 'built', 'optimized', 'streamlined', 'orchestrated',
    'spearheaded', 'pioneered', 'transformed', 'established', 'drove',
    'executed', 'accelerated', 'generated', 'maximized', 'enhanced'
]

QUANT_PATTERNS = [
    r'\d+%',  
    r'\d+\+',  
    r'[$€£]\d+',  
    r'\d+[xX]',  
    r'\d+\s*(million|billion|thousand|k|m|b)',
]
