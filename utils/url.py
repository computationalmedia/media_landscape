import tldextract

def reconstruct_url(url):

    url_domain = tldextract.extract(url).domain
    url_subdomain = tldextract.extract(url).subdomain
    url_suffix = tldextract.extract(url).suffix
    
    if url_subdomain == 'www' or url_subdomain == 'com' or url_subdomain == 'http' or url_subdomain == 'https':
        url_subdomain = ''

    if url_suffix == 'www' or url_suffix == 'com' or url_suffix == 'http' or url_suffix == 'https':
        url_suffix = ''

    url_reconstruct = url_subdomain 

    if url_domain != '':
        url_reconstruct += '.'+url_domain

    if url_suffix != '':
        url_reconstruct += '.'+url_suffix

    url_reconstruct = url_reconstruct.strip()
    
    if url_reconstruct[0] == '.':
        url_reconstruct = url_reconstruct[1:]
        
    return url_reconstruct.lower()


