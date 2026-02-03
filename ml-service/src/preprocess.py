# DOM feature extraction

import re
import math
from urllib.parse import urlparse
import numpy as np

class URLExtractor:
    """
    Sentinel Intelligence Layer: URL Feature Extraction
    Matches the 41-feature schema of the provided dataset.
    """
    
    def calculate_entropy(self, text):
        if not text:
            return 0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

    def extract_features(self, url):
        hostname = urlparse(url).netloc
        path = urlparse(url).path
        query = urlparse(url).query
        
        features = []
        
        # 1-5: Lengths and basic counts
        features.append(len(url)) # url_length
        features.append(url.count('.')) # number_of_dots_in_url
        features.append(1 if re.search(r'(\d)\1{2,}', url) else 0) # having_repeated_digits_in_url
        features.append(len(re.findall(r'\d', url))) # number_of_digits_in_url
        features.append(len(re.findall(r'[^a-zA-Z0-9]', url))) # number_of_special_char_in_url
        
        # 6-10: URL Char counts
        features.append(url.count('-')) # number_of_hyphens_in_url
        features.append(url.count('_')) # number_of_underline_in_url
        features.append(url.count('/')) # number_of_slash_in_url
        features.append(url.count('?')) # number_of_questionmark_in_url
        features.append(url.count('=')) # number_of_equal_in_url
        
        # 11-15: URL Special chars
        features.append(url.count('@')) # number_of_at_in_url
        features.append(url.count('$')) # number_of_dollar_in_url
        features.append(url.count('!')) # number_of_exclamation_in_url
        features.append(url.count('#')) # number_of_hashtag_in_url
        features.append(url.count('%')) # number_of_percent_in_url
        
        # 16-20: Domain features
        features.append(len(hostname)) # domain_length
        features.append(hostname.count('.')) # number_of_dots_in_domain
        features.append(hostname.count('-')) # number_of_hyphens_in_domain
        features.append(1 if re.search(r'[^a-zA-Z0-9.]', hostname) else 0) # having_special_characters_in_domain
        features.append(len(re.findall(r'[^a-zA-Z0-9.]', hostname))) # number_of_special_characters_in_domain
        
        # 21-25: Domain Digits & Subdomains
        features.append(1 if re.search(r'\d', hostname) else 0) # having_digits_in_domain
        features.append(len(re.findall(r'\d', hostname))) # number_of_digits_in_domain
        features.append(1 if re.search(r'(\d)\1{2,}', hostname) else 0) # having_repeated_digits_in_domain
        subdomains = hostname.split('.')[:-2]
        features.append(len(subdomains)) # number_of_subdomains
        features.append(1 if any('.' in s for s in subdomains) else 0) # having_dot_in_subdomain
        
        # 26-30: Subdomain details
        features.append(1 if any('-' in s for s in subdomains) else 0) # having_hyphen_in_subdomain
        avg_sub_len = np.mean([len(s) for s in subdomains]) if subdomains else 0
        features.append(avg_sub_len) # average_subdomain_length
        avg_sub_dots = np.mean([s.count('.') for s in subdomains]) if subdomains else 0
        features.append(avg_sub_dots) # average_number_of_dots_in_subdomain
        avg_sub_hyphens = np.mean([s.count('-') for s in subdomains]) if subdomains else 0
        features.append(avg_sub_hyphens) # average_number_of_hyphens_in_subdomain
        features.append(1 if any(re.search(r'[^a-zA-Z0-9]', s) for s in subdomains) else 0) # having_special_characters_in_subdomain
        
        # 31-35: Subdomain special chars/digits
        features.append(sum(len(re.findall(r'[^a-zA-Z0-9]', s)) for s in subdomains)) # number_of_special_characters_in_subdomain
        features.append(1 if any(re.search(r'\d', s) for s in subdomains) else 0) # having_digits_in_subdomain
        features.append(sum(len(re.findall(r'\d', s)) for s in subdomains)) # number_of_digits_in_subdomain
        features.append(1 if any(re.search(r'(\d)\1{2,}', s) for s in subdomains) else 0) # having_repeated_digits_in_subdomain
        features.append(1 if path else 0) # having_path
        
        # 36-41: Path/Query/Entropy
        features.append(len(path)) # path_length
        features.append(1 if query else 0) # having_query
        features.append(1 if urlparse(url).fragment else 0) # having_fragment
        features.append(1 if '#' in url else 0) # having_anchor
        features.append(self.calculate_entropy(url)) # entropy_of_url
        features.append(self.calculate_entropy(hostname)) # entropy_of_domain
        
        return np.array(features).reshape(1, -1)

# Example Usage
if __name__ == "__main__":
    extractor = URLExtractor()
    vec = extractor.extract_features("https://www.google.com/search?q=sentinel")
    print(f"Extracted Vector Shape: {vec.shape} (Expected: 1, 41)")