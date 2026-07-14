import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Swap Education and Certifications sections
# Find the start and end of both sections
edu_start = content.find('<!-- EDUCATION -->')
certs_start = content.find('<!-- CERTIFICATIONS -->')
contact_start = content.find('<!-- CONTACT -->')

if edu_start != -1 and certs_start != -1 and contact_start != -1:
    education_html = content[edu_start:certs_start]
    certs_html = content[certs_start:contact_start]
    
    # We will swap them. 
    # Current order: ... -> education_html -> certs_html -> CONTACT
    # New order: ... -> certs_html -> education_html -> CONTACT
    content = content[:edu_start] + certs_html + education_html + content[contact_start:]

# 2. Make certificates clickable links
# They are currently `<div class="edu-card rv cert-item">` or `<div class="edu-card rv cert-item hidden-cert" style="display:none;">`
# We'll change them to `<a href="#" class="edu-card rv cert-item"` etc, and change closing `</div>` of those specific cards to `</a>`.
# Using regex to find cert-item blocks
def repl_cert_div(match):
    tag = match.group(0)
    # Replace the opening <div with <a href="#" target="_blank" style="text-decoration:none; display:block; cursor:pointer;"
    tag = tag.replace('<div ', '<a href="#" target="_blank" style="text-decoration:none; display:block; cursor:pointer;" ')
    return tag

content = re.sub(r'<div class="edu-card rv cert-item[^>]*>', repl_cert_div, content)

# To replace the closing tags, we need to be careful. Since they are links now, let's just do a manual string replace in the certs_html block before we re-inject, or use a robust method.
# Since we already swapped them, let's just find the certs block again and replace.
# It's safer to do this specifically inside the certifications section.
c_start = content.find('<!-- CERTIFICATIONS -->')
e_start = content.find('<!-- EDUCATION -->')
if c_start != -1 and e_start != -1:
    certs_block = content[c_start:e_start]
    # In certs block, replace 6 `</div>` that correspond to the end of the edu-cards.
    # Actually, if we change the start to `<a`, the end must be `</a>`.
    # Let's just fix the certs block explicitly.
    certs_block = certs_block.replace('<div class="edu-card', '<a href="#" target="_blank" style="text-decoration:none; display:block; cursor:pointer;" class="edu-card')
    # Every cert card ends with `</div>` right before the next `<a` or `</div>\n  </div>` (the grid end).
    certs_block = re.sub(r'</div>(\s*<a href="#" target="_blank")', r'</a>\1', certs_block)
    # the last one
    certs_block = re.sub(r'</div>(\s*</div>\s*<div style="text-align:center;)', r'</a>\1', certs_block)
    
    content = content[:c_start] + certs_block + content[e_start:]

# 3. Fix GitHub button color in Projects
# In projects, the github link usually looks like:
# <a href="https://github.com/..." target="_blank" class="p-git"><svg ...>...</a>
# Let's find `.p-git` or github buttons. Let's look at the CSS for projects.
# Let's add inline styles for golden color to `.p-git` or similar.
# Wait, I don't know the exact class. I will inject CSS to style it.
golden_css = """
/* Make GitHub buttons in projects golden */
.proj-card .p-git,
.proj-card a[href*="github.com"] {
    background: rgba(251,191,36,0.1) !important;
    border-color: rgba(251,191,36,0.3) !important;
    color: #fbbf24 !important;
}
.proj-card a[href*="github.com"]:hover {
    background: rgba(251,191,36,0.2) !important;
    box-shadow: 0 4px 12px rgba(251,191,36,0.2) !important;
}
"""
content = content.replace('</style>', golden_css + '\n</style>')

# 4. Fix "Show More" button JS
# The button JS is currently bound to DOMContentLoaded or just inline.
# Let's replace the JS block.
old_js = """/* CERTIFICATIONS TOGGLE LOGIC */
(function(){
  const btn = document.getElementById('show-more-certs');
  if(!btn) return;
  btn.addEventListener('click', () => {
    const hidden = document.querySelectorAll('.hidden-cert');
    if(hidden.length === 0) return;
    
    const isHidden = hidden[0].style.display === 'none';
    hidden.forEach(el => {
      el.style.display = isHidden ? 'block' : 'none';
      if(isHidden) {
        el.style.animation = 'floatUp 0.6s ease forwards';
      }
    });
    btn.textContent = isHidden ? 'Show Less' : 'Show More Certificates';
  });
})();"""

new_js = """/* CERTIFICATIONS TOGGLE LOGIC */
(function(){
  // Use a slight delay or wait for load to ensure DOM is ready
  window.addEventListener('load', () => {
    const btn = document.getElementById('show-more-certs');
    if(!btn) return;
    
    // Check initial state correctly (inline styles)
    let isHidden = true; 
    
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const hidden = document.querySelectorAll('.hidden-cert');
      
      if(isHidden) {
        hidden.forEach(el => {
          el.style.display = 'block';
          el.style.animation = 'floatUp 0.6s ease forwards';
        });
        btn.textContent = 'Show Less';
        isHidden = false;
      } else {
        hidden.forEach(el => {
          el.style.display = 'none';
          el.style.animation = '';
        });
        btn.textContent = 'Show More Certificates';
        isHidden = true;
      }
      
      if(window.ScrollTrigger) window.ScrollTrigger.refresh();
    });
  });
})();"""

content = content.replace(old_js, new_js)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
with open('haseeb_portfolio_final.html', 'w', encoding='utf-8') as f:
    f.write(content)
