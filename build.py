import os
import glob
import markdown
import json
import re

def parse_markdown_file(filepath):
    """Extracts frontmatter and converts the body to HTML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    meta = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            meta_text = parts[1]
            body_markdown = parts[2].strip()
            for line in meta_text.strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    meta[key.strip()] = val.strip().strip('"').strip("'")
            body = markdown.markdown(body_markdown)
    return meta, body

def read_file(filepath):
    """Helper function to read files quickly."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def build_site():
    print("Starting the modular site build...")
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Read Master Templates & Components
    master_template = read_file(os.path.join(base_dir, 'templates', 'layout-main.html'))
    news_template = read_file(os.path.join(base_dir, 'templates', 'layout-news.html'))
    header = read_file(os.path.join(base_dir, 'components', 'header.html'))
    footer = read_file(os.path.join(base_dir, 'components', 'footer.html'))

    # 2. Read all 5 Homepage Sections
    sections_dir = os.path.join(base_dir, 'sections')
    s1_hero = read_file(os.path.join(sections_dir, '01-hero.html'))
    s2_links = read_file(os.path.join(sections_dir, '02-quick-links.html'))
    s3_about = read_file(os.path.join(sections_dir, '03-about-stats.html'))
    s4_news = read_file(os.path.join(sections_dir, '04-news-grid.html'))
    s5_cta = read_file(os.path.join(sections_dir, '05-cta-partners.html'))

    # 3. Process Markdown Content for News
    news_out_dir = os.path.join(base_dir, 'news')
    os.makedirs(news_out_dir, exist_ok=True)
    
    content_dir = os.path.join(base_dir, 'content')
    news_cards_html = ""
    
    for filename in os.listdir(content_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(content_dir, filename)
            meta, html_body = parse_markdown_file(filepath)
            
            title = meta.get('title', 'بدون عنوان')
            date = meta.get('date', '')
            image = meta.get('image', 'https://via.placeholder.com/800x400?text=No+Image')
            summary = meta.get('summary', 'متن خلاصه...')
            
            page_filename = filename.replace('.md', '.html')
            page_link = f"news/{page_filename}"

            # Create the small card for the homepage
            card_html = f"""
            <a href="{page_link}" class="news-card">
                <img src="{image}" alt="{title}" class="news-card-image">
                <div class="news-card-content">
                    <span class="news-meta">{date}</span>
                    <h3 style="margin-bottom: 10px; color: var(--color-dark);">{title}</h3>
                    <p style="color: var(--color-text-main);">{summary}</p>
                </div>
            </a>
            """
            news_cards_html += card_html

            # Create the dedicated standalone news page
            article_content = news_template.replace("{{ title }}", title)
            article_content = article_content.replace("{{ date }}", date)
            article_content = article_content.replace("{{ image }}", image)
            article_content = article_content.replace("{{ article_body }}", html_body)

            final_article_page = master_template.replace("{{ include 'components/header.html' }}", header)
            final_article_page = final_article_page.replace("{{ include 'components/footer.html' }}", footer)
            final_article_page = final_article_page.replace("{{ content }}", article_content)
            final_article_page = final_article_page.replace("{{ title }}", title)

            with open(os.path.join(news_out_dir, page_filename), 'w', encoding='utf-8') as f:
                f.write(final_article_page)

    # 4. Generate Individual Article Pages AND Homepage Cards
    md_files = glob.glob(os.path.join(base_dir, 'content', '*.md'))
    md_files.sort(reverse=True) # Newest first

    # Read the layout template
    with open(os.path.join(base_dir, 'templates', 'layout-news.html'), 'r', encoding='utf-8') as f:
        layout_news = f.read()

    news_cards_html = ""
    all_news_cards_html = ""

    for index, filepath in enumerate(md_files):
        filename = os.path.basename(filepath)
        page_filename = filename.replace('.md', '.html') 
        url = "./" + page_filename # Points to the root folder safely!
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        title = "بدون عنوان"
        image = "./assets/images/placeholder.jpg" # Fallback image
        html_content = content
        
        # 1. Extract the info from the Markdown file
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                html_content = parts[2] 
                
                for line in frontmatter.split('\n'):
                    if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                    if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()
                    
        # 2. GENERATE THE INDIVIDUAL ARTICLE PAGE
        final_article = layout_news.replace("{{ include 'components/header.html' }}", header)
        final_article = final_article.replace("{{ include 'components/footer.html' }}", footer)
        final_article = final_article.replace("{{ title }}", title)
        final_article = final_article.replace("{{ image }}", image)
        
        # Convert markdown table/text to HTML and inject it
        article_body = markdown.markdown(html_content)
        final_article = final_article.replace("{{ content }}", article_body)
        
        # Save directly to the root folder (base_dir) so CSS works perfectly!
        with open(os.path.join(base_dir, page_filename), 'w', encoding='utf-8') as f:
            f.write(final_article)

        # 3. GENERATE THE CARD HTML (Only if it's a newsletter!)
        if 'newsletter' in content:
            card_html = f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden;">
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-primary); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="color: var(--color-text-main); font-weight: bold; font-size: 0.95rem;">مشاهده کامل &larr;</span>
                    </div>
                </a>
            </div>
            """
            all_news_cards_html += card_html
            if index < 3: # Keep only the newest 3 for the homepage
                news_cards_html += card_html

                
    # Inject the generated cards into your Homepage News Section!
    s4_news_populated = s4_news.replace("{{ automated_news_cards }}", news_cards_html)

    # 5. Generate the Search Results Page (search.html)
    search_html_content = """
    <section class="section-padding container" style="min-height: 60vh;">
        <h1 class="section-title">نتایج جستجو</h1>
        
        <div style="background: var(--color-bg-white); padding: 50px 20px; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); text-align: center; border: 1px solid var(--color-border); max-width: 800px; margin: 0 auto;">
            <div style="margin-bottom: 30px;">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.5;">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </div>
            
            <h3 style="margin-bottom: 15px; color: var(--color-dark); font-size: 1.5rem;">
                نتایج جستجو برای: <span id="search-term" style="color: var(--color-secondary); font-weight: 900;"></span>
            </h3>
            
            <p style="color: var(--color-text-muted); font-size: 1.1rem; margin-bottom: 30px;">
                پایگاه داده جستجوی هوشمند سایت به زودی فعال خواهد شد. فعلاً می‌توانید از طریق منوی اصلی به بخش‌های مختلف دسترسی پیدا کنید.
            </p>
            
            <a href="index.html" class="btn-primary">بازگشت به صفحه اصلی</a>
        </div>
    </section>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const params = new URLSearchParams(window.location.search);
            const query = params.get('q');
            const termDisplay = document.getElementById('search-term');
            
            if (query) {
                termDisplay.innerText = '« ' + query + ' »';
            } else {
                termDisplay.innerText = 'چیزی وارد نشده';
            }
        });
    </script>
    """

    # 6. Generate the Board Members Page (board.html)
    board_html_content = """
    <section class="section-padding container" style="min-height: 70vh;">
        <div style="text-align: center; margin-bottom: 50px; padding: 0 20px;">
            <h1 class="section-title">لیست اعضای هیئت‌مدیره انجمن</h1>
            <p style="color: var(--color-text-main); font-size: 1.1rem; max-width: 900px; margin: 0 auto; line-height: 1.8;">
                انجمن علمی مهندسی و مدیریت پسماند ایران زیر نظر کمیسیون انجمن‌های علمی وزارت علوم، تحقیقات و فناوری، با حضور اساتید، کارشناسان، صاحب‌نظران و مدیران برجسته کشور و به منظور گسترش، پیشبرد و ارتقای علمی مدیریت پسماند و توسعه کیفی نیروهای متخصص و پژوهشی در زمینه‌های مهندسی محیط‌زیست و مدیریت پسماند تشکیل شده است. اسامی اعضای هیئت‌مدیره انجمن به شرح زیر می‌باشد:
            </p>
        </div>

        <div class="board-grid">
            <div class="board-card">
                <div class="board-img-wrapper">
                    <img src="./assets/images/board member/board-1.jpg" alt="دکتر عبدالرضا کرباسی" onerror="this.style.display='none'">
                </div>
                <div class="board-info">
                    <h3>دکتر عبدالرضا کرباسی</h3>
                    <p class="board-role">عضو هیئت‌مدیره و رئیس انجمن</p>
                </div>
            </div>
            <div class="board-card">
                <div class="board-img-wrapper">
                    <img src="./assets/images/board member/board-2.jpg" alt="دکتر رودابه سمیعی زفرقندی" onerror="this.style.display='none'">
                </div>
                <div class="board-info">
                    <h3>دکتر رودابه سمیعی زفرقندی</h3>
                    <p class="board-role">عضو هیئت‌مدیره و نایب‌رئیس</p>
                </div>
            </div>
            <div class="board-card">
                <div class="board-img-wrapper">
                    <img src="./assets/images/board member/board-3.jpg" alt="مهندس ناهید حسن‌زاده" onerror="this.style.display='none'">
                </div>
                <div class="board-info">
                    <h3>مهندس ناهید حسن‌زاده</h3>
                    <p class="board-role">عضو هیئت‌مدیره و خزانه‌دار</p>
                </div>
            </div>
            <div class="board-card">
                <div class="board-img-wrapper">
                    <img src="./assets/images/board member/board-4.jpg" alt="دکتر علیرضا عسگری" onerror="this.style.display='none'">
                </div>
                <div class="board-info">
                    <h3>دکتر علیرضا عسگری</h3>
                    <p class="board-role">عضو هیئت‌مدیره</p>
                </div>
            </div>
            <div class="board-card">
                <div class="board-img-wrapper">
                    <img src="./assets/images/board member/board-5.jpg" alt="مهندس حسین روستایی" onerror="this.style.display='none'">
                </div>
                <div class="board-info">
                    <h3>مهندس حسین روستایی</h3>
                    <p class="board-role">عضو هیئت‌مدیره</p>
                </div>
            </div>
            <div class="board-card">
                <div class="board-img-wrapper">
                    <img src="./assets/images/board member/board-6.jpg" alt="دکتر محمدعلی عبدلی" onerror="this.style.display='none'">
                </div>
                <div class="board-info">
                    <h3>دکتر محمدعلی عبدلی</h3>
                    <p class="board-role">بازرس</p>
                </div>
            </div>
        </div>
    </section>
    """

    final_board_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_board_page = final_board_page.replace("{{ include 'components/footer.html' }}", footer)
    final_board_page = final_board_page.replace("{{ content }}", board_html_content)
    final_board_page = final_board_page.replace("{{ title }}", "اعضای هیات مدیره")

    with open(os.path.join(base_dir, 'board.html'), 'w', encoding='utf-8') as f:
        f.write(final_board_page)

    # 7. Generate the News Archive Page (news.html)
    all_news_cards_html = ""
    for filepath in md_files: # Loop through ALL articles, not just 3
        filename = os.path.basename(filepath)
        url = "./" + filename.replace('.md', '.html')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        title = "بدون عنوان"
        image = "./assets/images/placeholder.jpg"
        
        for line in content.split('\n'):
            if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
            if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()
            if line.startswith('date:'): date = line.split(':', 1)[1].replace('"', '').strip()

        all_news_cards_html += f"""
        <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
            <a href="{url}" style="text-decoration: none; color: inherit; display: block;">
                <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden;">
                    <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                </div>
                <div style="padding: 25px 20px;">
                    <h3 style="font-size: 1.2rem; color: var(--color-primary); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                    <span style="color: var(--color-text-main); font-weight: bold; font-size: 0.95rem;">مشاهده کامل &larr;</span>
                </div>
            </a>
        </div>
        """

    news_page_content = f"""
    <section class="section-padding container" style="min-height: 70vh;">
        <div style="text-align: center; margin-bottom: 50px;">
            <h1 class="section-title">اخبار و رویدادها</h1>
            <p style="color: var(--color-text-main); font-size: 1.1rem; max-width: 800px; margin: 0 auto;">در این بخش می‌توانید آخرین اخبار، مقالات و رویدادهای انجمن را مشاهده کنید.</p>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">
            {all_news_cards_html}
        </div>
    </section>
    """

    final_news_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_news_page = final_news_page.replace("{{ include 'components/footer.html' }}", footer)
    final_news_page = final_news_page.replace("{{ content }}", news_page_content)
    final_news_page = final_news_page.replace("{{ title }}", "اخبار")

    with open(os.path.join(base_dir, 'news.html'), 'w', encoding='utf-8') as f:
        f.write(final_news_page)
    
    # Wrap the search content in our master template
    final_search_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_search_page = final_search_page.replace("{{ include 'components/footer.html' }}", footer)
    final_search_page = final_search_page.replace("{{ content }}", search_html_content)
    final_search_page = final_search_page.replace("{{ title }}", "جستجو")

    # Save it to the main folder
    with open(os.path.join(base_dir, 'search.html'), 'w', encoding='utf-8') as f:
        f.write(final_search_page)

    # =====================================================================
    # FINAL STEP: Stitch together and save the Homepage (index.html)
    # =====================================================================
    
    # 1. Combine all the sections (Notice we are using s4_news_populated!)
    index_body = s1_hero + s2_links + s3_about + s4_news_populated + s5_cta
    
    # 2. Inject it into your master layout template
    final_index = master_template.replace("{{ include 'components/header.html' }}", header)
    final_index = final_index.replace("{{ include 'components/footer.html' }}", footer)
    final_index = final_index.replace("{{ content }}", index_body)
    final_index = final_index.replace("{{ title }}", "خانه")
    
    # 3. Save the finished homepage to your main folder
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(final_index)

    # =====================================================================
    # 8. Generate the About Us Page (about.html)
    # =====================================================================
    about_html_content = """
    <section class="article-header" style="background-color: var(--color-primary); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container">
            <h1 style="font-size: 2.2rem; font-weight: 900; margin: 0;">درباره انجمن</h1>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 50vh; margin-top: 20px;">
        <div class="grid-2" style="align-items: start; gap: 60px;">
            
            <div>
                <h2 style="color: var(--color-primary); font-size: 1.8rem; margin-bottom: 20px; font-weight: 800; border-bottom: 3px solid var(--color-secondary); display: inline-block; padding-bottom: 10px;">تاریخچه و معرفی</h2>
                <p style="color: var(--color-text-main); font-size: 1.1rem; margin-bottom: 50px; text-align: justify; line-height: 2.2;">
                    انجمن علمی مهندسی و مدیریت پسماند ایران زیر نظر کمیسیون انجمن‌های علمی وزارت علوم، تحقیقات و فناوری، با حضور اساتید، کارشناسان، صاحب‌نظران و مدیران برجسته کشور در سال ۱۳۹۰ تاسیس شده است. هدف اصلی این انجمن، گسترش، پیشبرد و ارتقای علمی مدیریت پسماند و توسعه کیفی نیروهای متخصص و پژوهشی در زمینه‌های مهندسی محیط‌زیست می‌باشد.
                </p>

                <h2 style="color: var(--color-primary); font-size: 1.8rem; margin-bottom: 30px; font-weight: 800; border-bottom: 3px solid var(--color-secondary); display: inline-block; padding-bottom: 10px;">اهداف و رسالت‌ها</h2>
                <ul style="color: var(--color-text-main); font-size: 1.05rem; line-height: 2; padding-right: 0; list-style: none;">
                    <li style="margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                        <span style="color: var(--color-secondary); font-size: 1.2rem; margin-top: -2px;">✔</span>
                        <span>انجام تحقیقات علمی و فرهنگی در سطح ملی و بین‌المللی با محققان و متخصصانی که به گونه‌ای با مدیریت پسماند سر و کار دارند.</span>
                    </li>
                    <li style="margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                        <span style="color: var(--color-secondary); font-size: 1.2rem; margin-top: -2px;">✔</span>
                        <span>همکاری با نهادهای اجرایی و علمی در زمینه ارزیابی و بازنگری طرح‌ها و برنامه‌های مربوطه.</span>
                    </li>
                    <li style="margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                        <span style="color: var(--color-secondary); font-size: 1.2rem; margin-top: -2px;">✔</span>
                        <span>ترغیب و تشویق پژوهشگران و تجلیل از محققان و استادان ممتاز.</span>
                    </li>
                    <li style="margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                        <span style="color: var(--color-secondary); font-size: 1.2rem; margin-top: -2px;">✔</span>
                        <span>ارائه خدمات آموزشی و پژوهشی و برگزاری دوره‌های تخصصی کوتاه مدت.</span>
                    </li>
                    <li style="margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                        <span style="color: var(--color-secondary); font-size: 1.2rem; margin-top: -2px;">✔</span>
                        <span>برگزاری گردهمایی‌های علمی در سطح ملی، منطقه‌ای و بین‌المللی.</span>
                    </li>
                    <li style="margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
                        <span style="color: var(--color-secondary); font-size: 1.2rem; margin-top: -2px;">✔</span>
                        <span>انتشار کتب و نشریات علمی در زمینه مهندسی و مدیریت پسماند.</span>
                    </li>
                </ul>
            </div>

            <div style="background-color: var(--color-bg-light); border-radius: var(--radius-lg); padding: 40px; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); position: sticky; top: 120px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="./assets/images/logo.png" alt="لوگو انجمن مدیریت پسماند" style="max-width: 180px; margin-bottom: 20px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
                    <h3 style="color: var(--color-dark); font-size: 1.4rem; font-weight: 800;">انجمن مدیریت پسماند</h3>
                    <p style="color: var(--color-secondary); font-weight: bold; font-size: 1rem; margin-top: 5px;">تاسیس سال ۱۳۹۰</p>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    <a href="tel:02161113199" class="btn-outline" style="width: 100%; text-align: center; border-color: var(--color-border); color: var(--color-dark); display: flex; justify-content: center; align-items: center; gap: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                        <span dir="ltr">۰۲۱ - ۶۱۱۱۳۱۹۹</span>
                    </a>
                    <a href="mailto:anjomanpasmand@gmail.com" class="btn-outline" style="width: 100%; text-align: center; border-color: var(--color-border); color: var(--color-dark); display: flex; justify-content: center; align-items: center; gap: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                        ایمیل انجمن
                    </a>
                    <a href="https://t.me/anjomanpasmandiran" target="_blank" class="btn-primary" style="width: 100%; text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                        کانال تلگرام
                    </a>
                </div>
            </div>

        </div>
    </section>
    """

    final_about_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_about_page = final_about_page.replace("{{ include 'components/footer.html' }}", footer)
    final_about_page = final_about_page.replace("{{ content }}", about_html_content)
    final_about_page = final_about_page.replace("{{ title }}", "درباره ما")

    with open(os.path.join(base_dir, 'about.html'), 'w', encoding='utf-8') as f:
        f.write(final_about_page)

    # =====================================================================
    # 9. Generate the Courses Archive Page (courses.html)
    # =====================================================================
    course_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as courses
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a course!
        if 'دوره‌ها و کارگاه‌ها' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Course Card
            course_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: var(--color-primary); color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">دوره آموزشی</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: var(--color-primary); font-weight: bold; font-size: 0.95rem;">
                            مشاهده جزئیات و ثبت‌نام
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    courses_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">دوره‌ها و کارگاه‌های آموزشی</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">ارتقای سطح علمی و تخصصی با شرکت در جدیدترین دوره‌های مهندسی و مدیریت پسماند</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {course_cards_html if course_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر دوره جدیدی تعریف نشده است.</p>'}
        </div>
    </section>
    """

    # Inject everything into the master template and save
    final_courses_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_courses_page = final_courses_page.replace("{{ include 'components/footer.html' }}", footer)
    final_courses_page = final_courses_page.replace("{{ content }}", courses_page_html)
    final_courses_page = final_courses_page.replace("{{ title }}", "دوره‌ها و کارگاه‌ها")

    with open(os.path.join(base_dir, 'courses.html'), 'w', encoding='utf-8') as f:
        f.write(final_courses_page)


    # =====================================================================
    # 10. Generate the Sessions Archive Page (sessions.html)
    # =====================================================================
    session_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as sessions
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a session!
        if 'نشست‌ها' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Session Card
            session_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: var(--color-secondary); color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">نشست تخصصی</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: var(--color-primary); font-weight: bold; font-size: 0.95rem;">
                            مشاهده جزئیات نشست
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    sessions_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">نشست‌های تخصصی</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">بررسی چالش‌ها، ارائه راهکارها و تبادل نظر پیرامون مسائل روز مهندسی و مدیریت پسماند</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {session_cards_html if session_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر نشست جدیدی تعریف نشده است.</p>'}
        </div>
    </section>
    """

    # Inject everything into the master template and save
    final_sessions_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_sessions_page = final_sessions_page.replace("{{ include 'components/footer.html' }}", footer)
    final_sessions_page = final_sessions_page.replace("{{ content }}", sessions_page_html)
    final_sessions_page = final_sessions_page.replace("{{ title }}", "نشست‌ها")

    with open(os.path.join(base_dir, 'sessions.html'), 'w', encoding='utf-8') as f:
        f.write(final_sessions_page)

    # =====================================================================
    # 11. Generate the Committees Archive Page (committees.html)
    # =====================================================================
    committee_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as committees
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a committee!
        if 'کمیته‌های اصلی' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Committee Card
            committee_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #0b3b26; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">کمیته تخصصی</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: var(--color-primary); font-weight: bold; font-size: 0.95rem;">
                            آشنایی با اهداف و اعضا
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    committees_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">کمیته‌های اصلی انجمن</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">آشنایی با کارگروه‌ها و کمیته‌های تخصصی انجمن علمی مهندسی و مدیریت پسماند ایران</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {committee_cards_html if committee_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر کمیته‌ای تعریف نشده است.</p>'}
        </div>
    </section>
    """

    # Inject everything into the master template and save
    final_committees_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_committees_page = final_committees_page.replace("{{ include 'components/footer.html' }}", footer)
    final_committees_page = final_committees_page.replace("{{ content }}", committees_page_html)
    final_committees_page = final_committees_page.replace("{{ title }}", "کمیته‌های اصلی")

    with open(os.path.join(base_dir, 'committees.html'), 'w', encoding='utf-8') as f:
        f.write(final_committees_page)


    # =====================================================================
    # 12. Generate the Functional Search Page (search.html)
    # =====================================================================
    search_data_list = []

    # Loop through all markdown files to build the search database
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        filename = os.path.basename(filepath)
        page_url = "./" + filename.replace('.md', '.html')
        title = "بدون عنوان"

        # Extract title and body
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.split('\n'):
                    if line.startswith('title:'): 
                        title = line.split(':', 1)[1].replace('"', '').strip()
                body = parts[2]
            else:
                body = content
        else:
            body = content

        # Clean the text: First, completely remove <style> and <script> blocks and their contents
        clean_body = re.sub(r'<style[^>]*>.*?</style>', ' ', body, flags=re.IGNORECASE | re.DOTALL)
        clean_body = re.sub(r'<script[^>]*>.*?</script>', ' ', clean_body, flags=re.IGNORECASE | re.DOTALL)
        
        # Next, remove remaining normal HTML tags
        clean_body = re.sub(r'<[^>]+>', ' ', clean_body)
        
        # Finally, remove markdown symbols, curly braces, and newlines
        clean_body = re.sub(r'#|\*|-|>|\[|\]|\(|\)|\n|\{|\}', ' ', clean_body)
        clean_body = " ".join(clean_body.split())

        search_data_list.append({
            "title": title,
            "url": page_url,
            "content": clean_body
        })

    # Convert the python list into a Javascript-friendly JSON string
    search_json_string = json.dumps(search_data_list, ensure_ascii=False)

    # Build the Search HTML page with embedded Javascript
    search_page_html = f"""
    <section class="section-padding container" style="min-height: 60vh; margin-top: 100px; margin-bottom: 60px;">
        <div style="background: var(--color-bg-white); border-radius: 24px; padding: 50px; box-shadow: 0 15px 40px rgba(11, 59, 38, 0.08); border: 1px solid var(--color-border); max-width: 900px; margin: 0 auto;">
            
            <div style="text-align: center; margin-bottom: 40px;">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="var(--color-secondary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 15px; opacity: 0.8;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                <h1 style="font-size: 2rem; font-weight: 900; color: var(--color-dark); margin: 0;">نتایج جستجو</h1>
                <h3 id="search-query-display" style="font-size: 1.2rem; color: var(--color-text-main); margin-top: 15px;">در حال جستجو...</h3>
            </div>

            <div id="search-results" style="display: flex; flex-direction: column; gap: 20px;">
                </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="index.html" style="color: var(--color-primary); font-weight: bold; text-decoration: none;">بازگشت به صفحه اصلی &larr;</a>
            </div>

        </div>
    </section>

    <script>
        // Load the database generated by Python
        const searchDatabase = {search_json_string};
        
        // Get the search query from the URL (e.g., ?q=پلاستیک)
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');
        
        const displayElement = document.getElementById('search-query-display');
        const resultsContainer = document.getElementById('search-results');

        if (query && query.trim() !== '') {{
            displayElement.innerHTML = `نتایج جستجو برای: <span style="color: var(--color-primary);">«${{query}}»</span>`;
            
            const lowerCaseQuery = query.toLowerCase().trim();
            
            // Filter the database
            const matchedResults = searchDatabase.filter(item => 
                item.title.toLowerCase().includes(lowerCaseQuery) || 
                item.content.toLowerCase().includes(lowerCaseQuery)
            );

            // Render Results
            if (matchedResults.length > 0) {{
                let resultsHTML = '';
                matchedResults.forEach(res => {{
                    // Create a small preview snippet (approx 150 characters)
                    let snippet = res.content.substring(0, 180) + '...';
                    
                    resultsHTML += `
                    <a href="${{res.url}}" style="text-decoration: none; color: inherit; display: block;">
                        <div style="border: 1px solid var(--color-border); border-radius: 16px; padding: 25px; background: #fafdfb; transition: all 0.3s ease;">
                            <h3 style="color: var(--color-primary); margin: 0 0 10px 0; font-size: 1.3rem; font-weight: 800;">${{res.title}}</h3>
                            <p style="color: var(--color-text-main); margin: 0; font-size: 1rem; line-height: 1.8;">${{snippet}}</p>
                        </div>
                    </a>`;
                }});
                resultsContainer.innerHTML = resultsHTML;
                
                // Add hover effect via JS since it's injected
                const cards = resultsContainer.querySelectorAll('div');
                cards.forEach(card => {{
                    card.addEventListener('mouseenter', () => {{
                        card.style.transform = 'translateY(-4px)';
                        card.style.boxShadow = '0 10px 25px rgba(11, 59, 38, 0.1)';
                        card.style.borderColor = 'var(--color-primary)';
                    }});
                    card.addEventListener('mouseleave', () => {{
                        card.style.transform = 'translateY(0)';
                        card.style.boxShadow = 'none';
                        card.style.borderColor = 'var(--color-border)';
                    }});
                }});

            }} else {{
                resultsContainer.innerHTML = `<div style="text-align: center; padding: 30px; color: var(--color-text-muted); font-size: 1.1rem;">هیچ نتیجه‌ای برای <strong>«${{query}}»</strong> یافت نشد. لطفاً کلمات دیگری را امتحان کنید.</div>`;
            }}
            
        }} else {{
            displayElement.innerHTML = 'لطفاً یک کلمه برای جستجو وارد کنید.';
            resultsContainer.innerHTML = '';
        }}
    </script>
    """

    # Inject into master template and save
    final_search_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_search_page = final_search_page.replace("{{ include 'components/footer.html' }}", footer)
    final_search_page = final_search_page.replace("{{ content }}", search_page_html)
    final_search_page = final_search_page.replace("{{ title }}", "جستجو")

    with open(os.path.join(base_dir, 'search.html'), 'w', encoding='utf-8') as f:
        f.write(final_search_page)

    # =====================================================================
    # 13. Generate the Waste Management Hub Page (waste-management.html)
    # =====================================================================
    waste_articles_html = ""

    # Loop through all markdown files and pick the ones tagged as 'مدیریت پسماند'
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it has the general waste management tag
        if 'مدیریت پسماند' in content and '---' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')
            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.split('\n'):
                    if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                    if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            waste_articles_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden; position: relative;">
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: var(--color-primary); font-weight: bold; font-size: 0.95rem;">
                            مطالعه مطلب
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout (4 Sub-category Cards + Dynamic Articles)
    waste_hub_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">مدیریت پسماند</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">پورتال جامع قوانین، فناوری‌ها، شرکت‌های فعال و سیستم‌های یکپارچه</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="margin-top: 40px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 25px;">
            
            <a href="waste-law.html" style="text-decoration: none; display: block; background: #fff; border: 1px solid var(--color-border); border-radius: 20px; padding: 40px 20px; text-align: center; box-shadow: var(--shadow-sm); transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-8px)'; this.style.borderColor='var(--color-primary)';" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='var(--color-border)';">
                <div style="width: 70px; height: 70px; background: #E8F0EA; color: var(--color-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M3 21h18"/><path d="M9 10a3 3 0 1 0-6 0c0 1.66 1.34 3 3 3s3-1.34 3-3Z"/><path d="M21 10a3 3 0 1 0-6 0c0 1.66 1.34 3 3 3s3-1.34 3-3Z"/><path d="M12 6h9"/><path d="M3 6h9"/></svg>
                </div>
                <h3 style="color: var(--color-dark); font-size: 1.3rem; margin-bottom: 10px; font-weight: 900;">قانون مدیریت پسماندها</h3>
                <p style="color: var(--color-text-main); font-size: 0.95rem; line-height: 1.8; margin:0;">بررسی قوانین، مقررات و دستورالعمل‌های اجرایی</p>
            </a>

            <a href="waste-technology.html" style="text-decoration: none; display: block; background: #fff; border: 1px solid var(--color-border); border-radius: 20px; padding: 40px 20px; text-align: center; box-shadow: var(--shadow-sm); transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-8px)'; this.style.borderColor='var(--color-primary)';" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='var(--color-border)';">
                <div style="width: 70px; height: 70px; background: #E8F0EA; color: var(--color-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>
                </div>
                <h3 style="color: var(--color-dark); font-size: 1.3rem; margin-bottom: 10px; font-weight: 900;">فناوری‌های مدیریت</h3>
                <p style="color: var(--color-text-main); font-size: 0.95rem; line-height: 1.8; margin:0;">آشنایی با تکنولوژی‌ها و نوآوری‌های روز دنیا</p>
            </a>

            <a href="waste-companies.html" style="text-decoration: none; display: block; background: #fff; border: 1px solid var(--color-border); border-radius: 20px; padding: 40px 20px; text-align: center; box-shadow: var(--shadow-sm); transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-8px)'; this.style.borderColor='var(--color-primary)';" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='var(--color-border)';">
                <div style="width: 70px; height: 70px; background: #E8F0EA; color: var(--color-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>
                </div>
                <h3 style="color: var(--color-dark); font-size: 1.3rem; margin-bottom: 10px; font-weight: 900;">شرکت‌های فعال</h3>
                <p style="color: var(--color-text-main); font-size: 0.95rem; line-height: 1.8; margin:0;">معرفی سازمان‌ها و شرکت‌های حوزه مدیریت پسماند</p>
            </a>

            <a href="integrated-system.html" style="text-decoration: none; display: block; background: #fff; border: 1px solid var(--color-border); border-radius: 20px; padding: 40px 20px; text-align: center; box-shadow: var(--shadow-sm); transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-8px)'; this.style.borderColor='var(--color-primary)';" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='var(--color-border)';">
                <div style="width: 70px; height: 70px; background: #E8F0EA; color: var(--color-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                </div>
                <h3 style="color: var(--color-dark); font-size: 1.3rem; margin-bottom: 10px; font-weight: 900;">سیستم یکپارچه</h3>
                <p style="color: var(--color-text-main); font-size: 0.95rem; line-height: 1.8; margin:0;">پلتفرم‌ها و راهکارهای نرم‌افزاری مدیریت جامع</p>
            </a>

        </div>
    </section>

    <section class="section-padding container" style="margin-bottom: 60px; border-top: 1px dashed var(--color-border); padding-top: 50px;">
        <h2 style="text-align: center; margin-bottom: 40px; color: var(--color-dark); font-weight: 900; font-size: 1.8rem;">آخرین مقالات و اخبار این حوزه</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {waste_articles_html if waste_articles_html else '<p style="text-align: center; grid-column: 1/-1; color: var(--color-text-muted); font-size: 1.1rem;">در حال حاضر مطلب جدیدی در این بخش منتشر نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_waste_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_waste_page = final_waste_page.replace("{{ include 'components/footer.html' }}", footer)
    final_waste_page = final_waste_page.replace("{{ content }}", waste_hub_html)
    final_waste_page = final_waste_page.replace("{{ title }}", "مدیریت پسماند")

    with open(os.path.join(base_dir, 'waste-management.html'), 'w', encoding='utf-8') as f:
        f.write(final_waste_page)
    
    # =====================================================================
    # 14. Generate the Waste Law Archive Page (waste-law.html)
    # =====================================================================
    law_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "قانون پسماند"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a law article!
        if 'قانون پسماند' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Law Card
            law_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid var(--color-secondary); overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #334155; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">قوانین و مقررات</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: var(--color-primary); font-weight: bold; font-size: 0.95rem;">
                            مطالعه کامل تحلیل
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    law_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">قانون مدیریت پسماندها</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">مجموعه قوانین، آیین‌نامه‌های اجرایی و تحلیل‌های حقوقی پیرامون مدیریت پسماند</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {law_cards_html if law_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر مطلبی در این بخش منتشر نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_law_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_law_page = final_law_page.replace("{{ include 'components/footer.html' }}", footer)
    final_law_page = final_law_page.replace("{{ content }}", law_page_html)
    final_law_page = final_law_page.replace("{{ title }}", "قانون مدیریت پسماندها")

    with open(os.path.join(base_dir, 'waste-law.html'), 'w', encoding='utf-8') as f:
        f.write(final_law_page)
    
    # =====================================================================
    # 15. Generate the Waste Technology Archive Page (waste-technology.html)
    # =====================================================================
    tech_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "فناوری پسماند"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a technology article!
        if 'فناوری پسماند' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Technology Card
            tech_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid #0ea5e9; overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #0ea5e9; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.25);">فناوری و نوآوری</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: #0ea5e9; font-weight: bold; font-size: 0.95rem;">
                            بررسی تکنولوژی
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    tech_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">فناوری‌های مدیریت پسماند</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">آشنایی با جدیدترین تکنولوژی‌ها، تجهیزات و نوآوری‌های علمی در پردازش و بازیافت پسماند</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {tech_cards_html if tech_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر مطلبی در این بخش منتشر نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_tech_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_tech_page = final_tech_page.replace("{{ include 'components/footer.html' }}", footer)
    final_tech_page = final_tech_page.replace("{{ content }}", tech_page_html)
    final_tech_page = final_tech_page.replace("{{ title }}", "فناوری‌های مدیریت پسماند")

    with open(os.path.join(base_dir, 'waste-technology.html'), 'w', encoding='utf-8') as f:
        f.write(final_tech_page)

    # =====================================================================
    # 16. Generate the Waste Companies Archive Page (waste-companies.html)
    # =====================================================================
    companies_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "شرکت‌های پسماند"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a company profile!
        if 'شرکت‌های پسماند' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Company Card
            companies_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid #8b5cf6; overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #8b5cf6; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(139, 92, 246, 0.25);">معرفی شرکت</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: #8b5cf6; font-weight: bold; font-size: 0.95rem;">
                            مشاهده پروفایل شرکت
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    companies_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">شرکت‌های فعال در حوزه پسماند</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">دایرکتوری جامع سازمان‌ها، پیمانکاران و شرکت‌های دانش‌بنیان فعال در صنعت محیط‌زیست</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {companies_cards_html if companies_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر شرکتی در این بخش معرفی نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_companies_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_companies_page = final_companies_page.replace("{{ include 'components/footer.html' }}", footer)
    final_companies_page = final_companies_page.replace("{{ content }}", companies_page_html)
    final_companies_page = final_companies_page.replace("{{ title }}", "شرکت‌های فعال")

    with open(os.path.join(base_dir, 'waste-companies.html'), 'w', encoding='utf-8') as f:
        f.write(final_companies_page)

    # =====================================================================
    # 17. Generate the Integrated Systems Archive Page (integrated-system.html)
    # =====================================================================
    system_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "سیستم یکپارچه"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's an integrated system article!
        if 'سیستم یکپارچه' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual System Card
            system_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid #0d9488; overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #0d9488; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(13, 148, 136, 0.25);">نرم‌افزار و پلتفرم</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: #0d9488; font-weight: bold; font-size: 0.95rem;">
                            معرفی سامانه
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    system_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">سیستم‌های یکپارچه مدیریت پسماند</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">پلتفرم‌ها، راهکارهای نرم‌افزاری و سیستم‌های هوشمند برای مدیریت جامع و یکپارچه</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {system_cards_html if system_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر سامانه‌ای در این بخش معرفی نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_system_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_system_page = final_system_page.replace("{{ include 'components/footer.html' }}", footer)
    final_system_page = final_system_page.replace("{{ content }}", system_page_html)
    final_system_page = final_system_page.replace("{{ title }}", "سیستم‌های یکپارچه")

    with open(os.path.join(base_dir, 'integrated-system.html'), 'w', encoding='utf-8') as f:
        f.write(final_system_page)

    # =====================================================================
    # 18. Generate the Publications Archive Page (publications.html)
    # =====================================================================
    pub_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "انتشارات"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a publication!
        if 'انتشارات' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Publication Card
            pub_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 280px; background-color: #fff7ed; border-bottom: 2px solid #ea580c; overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #ea580c; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(234, 88, 12, 0.25);">معرفی کتاب</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: contain; padding: 20px;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: #ea580c; font-weight: bold; font-size: 0.95rem;">
                            مشاهده و تهیه کتاب
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    pub_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">انتشارات و مقالات</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">کتابخانه دیجیتال شامل جدیدترین کتب تخصصی، مقالات علمی و نشریات حوزه محیط‌زیست</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {pub_cards_html if pub_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر اثری در این بخش منتشر نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_pub_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_pub_page = final_pub_page.replace("{{ include 'components/footer.html' }}", footer)
    final_pub_page = final_pub_page.replace("{{ content }}", pub_page_html)
    final_pub_page = final_pub_page.replace("{{ title }}", "انتشارات")

    with open(os.path.join(base_dir, 'publications.html'), 'w', encoding='utf-8') as f:
        f.write(final_pub_page)

    # =====================================================================
    # 18. Generate the Conferences Archive Page (conferences.html)
    # =====================================================================
    conference_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "کنفرانس‌ها"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a conference article!
        if 'کنفرانس‌ها' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Conference Card
            conference_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid #4f46e5; overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #4f46e5; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);">رویداد علمی</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: #4f46e5; font-weight: bold; font-size: 0.95rem;">
                            اطلاعات کنفرانس و فراخوان
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    conferences_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">کنفرانس‌ها و همایش‌ها</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">فراخوان مقالات، رویدادهای ملی و بین‌المللی، و گردهمایی‌های تخصصی مهندسی و مدیریت پسماند</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {conference_cards_html if conference_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر رویداد جدیدی در این بخش تعریف نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_conferences_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_conferences_page = final_conferences_page.replace("{{ include 'components/footer.html' }}", footer)
    final_conferences_page = final_conferences_page.replace("{{ content }}", conferences_page_html)
    final_conferences_page = final_conferences_page.replace("{{ title }}", "کنفرانس‌ها و همایش‌ها")

    with open(os.path.join(base_dir, 'conferences.html'), 'w', encoding='utf-8') as f:
        f.write(final_conferences_page)
    
    # =====================================================================
    # 19. Generate the Branches Archive Page (branches.html)
    # =====================================================================
    branch_cards_html = ""

    # Loop through all markdown files and ONLY pick the ones tagged as "شعب استانی"
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a branch article!
        if 'شعب استانی' in content:
            filename = os.path.basename(filepath)
            page_url = "./" + filename.replace('.md', '.html')

            title = "بدون عنوان"
            image = "./assets/images/placeholder.jpg"

            # Extract title and image
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if line.startswith('title:'): title = line.split(':', 1)[1].replace('"', '').strip()
                        if line.startswith('image:'): image = line.split(':', 1)[1].replace('"', '').strip()

            # Build the individual Branch Card
            branch_cards_html += f"""
            <div style="background: var(--color-bg-white); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); transition: transform 0.3s ease;">
                <a href="{page_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="width: 100%; height: 220px; background-color: #E8F0EA; border-bottom: 2px solid #ea580c; overflow: hidden; position: relative;">
                        <span style="position: absolute; top: 15px; right: 15px; background: #ea580c; color: white; padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; z-index: 2; box-shadow: 0 4px 10px rgba(234, 88, 12, 0.25);">شعبه استانی</span>
                        <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">
                    </div>
                    <div style="padding: 25px 20px;">
                        <h3 style="font-size: 1.2rem; color: var(--color-dark); margin-bottom: 15px; line-height: 1.6; font-weight: 800;">{title}</h3>
                        <span style="display: inline-flex; align-items: center; gap: 8px; color: #ea580c; font-weight: bold; font-size: 0.95rem;">
                            اطلاعات تماس و آدرس
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                        </span>
                    </div>
                </a>
            </div>
            """

    # Build the full page layout
    branches_page_html = f"""
    <section class="article-header" style="background: linear-gradient(135deg, var(--color-primary) 0%, #0b3b26 100%); color: var(--color-bg-white); padding: 80px 20px 40px; text-align: center; margin-top: 80px;">
        <div class="container" style="position: relative; z-index: 2;">
            <h1 style="font-size: 2.4rem; font-weight: 900; margin: 0; color: #fff;">شعب استانی انجمن</h1>
            <p style="font-size: 1.15rem; color: rgba(255,255,255,0.9); margin-top: 15px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.8;">ارتباط با نمایندگان، دفاتر منطقه‌ای و شبکه‌ی گسترده‌ی انجمن در سراسر کشور</p>
        </div>
        <div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: hidden; pointer-events: none;">
            <div style="position: absolute; top: -50px; right: 10%; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -80px; left: 5%; width: 250px; height: 250px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        </div>
    </section>

    <section class="section-padding container" style="min-height: 45vh; margin-top: 40px; margin-bottom: 60px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
            {branch_cards_html if branch_cards_html else '<p style="text-align: center; grid-column: 1/-1; font-size: 1.2rem; color: var(--color-text-muted); font-weight: bold;">در حال حاضر شعبه‌ای در این بخش ثبت نشده است.</p>'}
        </div>
    </section>
    """

    # Inject into master template and save
    final_branches_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_branches_page = final_branches_page.replace("{{ include 'components/footer.html' }}", footer)
    final_branches_page = final_branches_page.replace("{{ content }}", branches_page_html)
    final_branches_page = final_branches_page.replace("{{ title }}", "شعب استانی")

    with open(os.path.join(base_dir, 'branches.html'), 'w', encoding='utf-8') as f:
        f.write(final_branches_page)
    
    # =====================================================================
    # 20. Generate the Secure Membership Page (membership.html)
    # =====================================================================
    membership_page_html = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.0.0/css/flag-icons.min.css" />
    
    <style>
        .membership-wrap {
            direction: rtl;
            font-family: 'Vazirmatn', Tahoma, sans-serif !important;
            background: #f8fafc;
            padding: 60px 20px;
            min-height: 80vh;
        }
        .portal-container {
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 20px 50px rgba(11, 59, 38, 0.08);
            overflow: hidden;
        }
        
        /* Tabs Header */
        .tabs-header {
            display: flex;
            background: #e2e8f0;
            border-bottom: 2px solid #cbd5e1;
            flex-wrap: wrap;
        }
        .tab-btn {
            flex: 1;
            min-width: 200px;
            padding: 20px 10px;
            border: none;
            background: transparent;
            font-family: 'Vazirmatn', Tahoma, sans-serif !important;
            font-size: 1.15rem;
            font-weight: 900;
            color: #64748b;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .tab-btn.active {
            background: #ffffff;
            color: var(--color-primary);
            box-shadow: inset 0 4px 0 var(--color-primary);
        }
        .tab-btn:hover:not(.active) {
            background: #f1f5f9;
            color: var(--color-dark);
        }

        .tab-content {
            display: none;
            padding: 40px 50px;
            animation: fadeIn 0.4s ease;
        }
        .tab-content.active { display: block; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Form Controls */
        .input-group { margin-bottom: 25px; text-align: right; }
        .input-group label { display: block; margin-bottom: 8px; font-weight: bold; color: var(--color-dark); }
        .input-control {
            width: 100%; padding: 15px 20px; border: 2px solid #e2e8f0; border-radius: 12px;
            font-family: 'Vazirmatn', Tahoma, sans-serif !important; font-size: 1.05rem; transition: all 0.3s ease; background: #f8fafc;
        }
        .input-control:focus { border-color: var(--color-primary); background: #ffffff; outline: none; box-shadow: 0 0 0 4px rgba(11, 59, 38, 0.1); }
        
        /* Custom Mobile Input with Lipis Flag Icons */
        .mobile-wrapper { display: flex; direction: ltr; align-items: stretch; }
        .country-select-container {
            display: flex;
            align-items: center;
            background: #e2e8f0;
            border-radius: 12px 0 0 12px;
            padding: 0 15px;
            border: 2px solid #e2e8f0;
            border-right: none;
            position: relative;
        }
        .country-select-container .fi {
            font-size: 1.4rem;
            border-radius: 3px;
        }
        .country-select-container select {
            border: none;
            background: transparent;
            font-family: 'Vazirmatn', Tahoma, sans-serif !important;
            font-weight: bold;
            font-size: 1rem;
            margin-left: 8px;
            outline: none;
            cursor: pointer;
            color: var(--color-dark);
            direction: rtl; 
        }
        .mobile-input {
            border-radius: 0 12px 12px 0;
            flex: 1;
            text-align: left;
            direction: ltr;
        }

        /* Buttons */
        .btn-group { display: flex; justify-content: space-between; margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 30px; }
        .btn {
            padding: 12px 30px; border-radius: 50px; font-size: 1.1rem; font-weight: bold; 
            font-family: 'Vazirmatn', Tahoma, sans-serif !important;
            cursor: pointer; border: none; transition: all 0.3s ease; display: inline-flex; align-items: center; justify-content: center; gap: 10px;
        }
        .btn-prev { background: #e2e8f0; color: #475569; }
        .btn-prev:hover { background: #cbd5e1; }
        .btn-next, .btn-submit { background: var(--color-primary); color: #ffffff; }
        .btn-next:hover, .btn-submit:hover:not(:disabled) { background: #082f1d; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(11, 59, 38, 0.2); }
        .btn-submit:disabled { background: #94a3b8; cursor: not-allowed; transform: none; box-shadow: none; }

        /* Payment Box */
        .payment-box { background: #f0f9ff; border: 2px dashed #0284c7; border-radius: 16px; padding: 25px; text-align: center; margin-bottom: 25px; transition: all 0.3s ease; }
        .payment-box h4 { color: #0369a1; margin: 0 0 10px 0; font-size: 1.3rem; }
        .payment-box p { margin: 5px 0; font-size: 1.1rem; }
        .payment-box .card-number { font-size: 1.8rem; font-weight: 900; letter-spacing: 2px; color: #104e8b; margin: 15px 0; direction: ltr; font-family: 'Vazirmatn', Tahoma, sans-serif !important; }

        /* Success/Error Modals */
        .alert-box { display: none; padding: 20px; border-radius: 12px; margin-top: 20px; text-align: center; font-weight: bold; font-size: 1.1rem; }
        .alert-success { background: #dcfce7; border: 1px solid #bbf7d0; color: #166534; }
        .alert-error { background: #fee2e2; border: 1px solid #fecaca; color: #991b1b; }

        /* Status Result Box */
        .status-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 30px; margin-top: 30px; display: none; }
        .status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .status-item { background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #f1f5f9; }
        .status-item span { display: block; font-size: 0.9rem; color: #64748b; margin-bottom: 5px; }
        .status-item strong { font-size: 1.2rem; color: var(--color-dark); font-weight: 900; }
        
        .loading-spinner { display: none; text-align: center; margin-top: 20px; color: var(--color-primary); font-weight: bold; }

        @media only screen and (max-width: 600px) {
            .tab-content { padding: 30px 20px; }
            .status-grid { grid-template-columns: 1fr; }
        }
    </style>

    <section class="membership-wrap">
        <div class="portal-container">
            
            <div class="tabs-header">
                <button class="tab-btn active" onclick="switchTab('individual')">عضویت حقیقی (افراد)</button>
                <button class="tab-btn" onclick="switchTab('corporate')">عضویت حقوقی (شرکت‌ها)</button>
                <button class="tab-btn" onclick="switchTab('status')">پیگیری وضعیت ثبت‌نام</button>
            </div>

            <div id="tab-individual" class="tab-content active">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: var(--color-primary); margin: 0 0 10px;">درخواست عضویت حقیقی</h2>
                    <p style="color: #64748b; margin:0;">جهت پیوستن به انجمن، فرم زیر را در ۳ مرحله تکمیل نمایید.</p>
                </div>

                <form id="ind-form" enctype="multipart/form-data">
                    <input type="hidden" name="access_key" value="0ddc649f-6c8e-4e32-810e-cb92ea65f7bf">
                    <input type="hidden" name="subject" value="درخواست عضویت حقیقی جدید">
                    
                    <div id="ind-step-1" class="form-step active">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                            <div class="input-group">
                                <label>نام و نام خانوادگی (فقط فارسی) *</label>
                                <input type="text" name="نام" class="input-control" required oninput="validatePersian(this)">
                            </div>
                            <div class="input-group">
                                <label>کد ملی (۱۰ رقم) *</label>
                                <input type="text" name="کد_ملی" class="input-control" required maxlength="10" placeholder="۰۰۱۲۳۴۵۶۷۸" oninput="formatNationalId(this)">
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                            <div class="input-group">
                                <label>شماره موبایل *</label>
                                <div class="mobile-wrapper">
                                    <div class="country-select-container">
                                        <span id="flag-ind" class="fi fi-ir"></span>
                                        <select name="کد_کشور" onchange="document.getElementById('flag-ind').className = 'fi fi-' + this.options[this.selectedIndex].getAttribute('data-cc')">
                                            <option value="+98" data-cc="ir">ایران (+۹۸)</option>
                                            <option value="+1" data-cc="us">آمریکا (+۱)</option>
                                            <option value="+1" data-cc="ca">کانادا (+۱)</option>
                                            <option value="+44" data-cc="gb">انگلیس (+۴۴)</option>
                                            <option value="+49" data-cc="de">آلمان (+۴۹)</option>
                                            <option value="+33" data-cc="fr">فرانسه (+۳۳)</option>
                                            <option value="+90" data-cc="tr">ترکیه (+۹۰)</option>
                                            <option value="+971" data-cc="ae">امارات (+۹۷۱)</option>
                                            <option value="+964" data-cc="iq">عراق (+۹۶۴)</option>
                                            <option value="+61" data-cc="au">استرالیا (+۶۱)</option>
                                        </select>
                                    </div>
                                    <input type="text" name="موبایل" class="input-control mobile-input" required placeholder="۹۱۲۰۵۴۳۵۸۷" oninput="formatMobile(this)">
                                </div>
                            </div>
                            <div class="input-group">
                                <label>ایمیل *</label>
                                <input type="email" name="ایمیل" class="input-control" dir="ltr" style="text-align:left;" required>
                            </div>
                        </div>
                        <div class="btn-group" style="justify-content: flex-end;">
                            <button type="button" class="btn btn-next" onclick="nextStep('ind', 1)">مرحله بعدی &larr;</button>
                        </div>
                    </div>

                    <div id="ind-step-2" class="form-step" style="display:none;">
                        <div class="input-group">
                            <label>وضعیت تحصیلی *</label>
                            <select id="edu_status" name="وضعیت_تحصیلی" class="input-control" required onchange="handleStudentStatus()">
                                <option value="" disabled selected>انتخاب کنید...</option>
                                <option value="فارغ التحصیل">فارغ‌التحصیل / شاغل</option>
                                <option value="دانشجو">دانشجو (در حال تحصیل)</option>
                            </select>
                        </div>
                        
                        <div id="student-fields" style="display:none; background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fde047; margin-bottom: 25px;">
                            <div class="input-group">
                                <label style="color: #a16207;">مقطع دانشجویی *</label>
                                <select id="student_level" name="مقطع_دانشجویی" class="input-control" style="background: #fff;" onchange="handleStudentStatus()">
                                    <option value="" disabled selected>انتخاب مقطع...</option>
                                    <option value="دانشجوی کاردانی">دانشجوی کاردانی</option>
                                    <option value="دانشجوی کارشناسی">دانشجوی کارشناسی</option>
                                    <option value="دانشجوی کارشناسی ارشد">دانشجوی کارشناسی ارشد</option>
                                    <option value="دانشجوی دکتری تخصصی">دانشجوی دکتری تخصصی</option>
                                    <option value="دانشجوی پست دکتری">دانشجوی پست دکتری</option>
                                </select>
                            </div>
                            <div class="input-group" style="margin-bottom:0;">
                                <label style="color: #a16207;">تصویر کارت دانشجویی معتبر (حداکثر ۲ مگابایت) *</label>
                                <input type="file" id="student_card_img" name="کارت_دانشجویی" class="input-control" accept="image/*,.pdf" style="background: #fff;">
                            </div>
                        </div>

                        <div id="grad-fields" style="display:none;">
                            <div class="input-group">
                                <label>آخرین مقطع فارغ‌التحصیلی *</label>
                                <select id="grad_level" name="مقطع_فارغ_التحصیلی" class="input-control" onchange="handleStudentStatus()">
                                    <option value="" disabled selected>انتخاب مقطع...</option>
                                    <option value="دیپلم">دیپلم</option>
                                    <option value="کاردانی">کاردانی</option>
                                    <option value="کارشناسی">کارشناسی</option>
                                    <option value="کارشناسی ارشد">کارشناسی ارشد</option>
                                    <option value="دکتری تخصصی">دکتری تخصصی</option>
                                </select>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                            <div class="input-group">
                                <label>رشته تحصیلی *</label>
                                <input type="text" name="رشته_تحصیلی" class="input-control" required>
                            </div>
                            <div class="input-group">
                                <label>سمت / شغل *</label>
                                <input type="text" id="job_title_input" name="سمت_شغل" class="input-control" required>
                            </div>
                        </div>

                        <div class="btn-group">
                            <button type="button" class="btn btn-prev" onclick="prevStep('ind', 2)">&rarr; مرحله قبلی</button>
                            <button type="button" class="btn btn-next" onclick="nextStep('ind', 2)">مرحله بعدی &larr;</button>
                        </div>
                    </div>

                    <div id="ind-step-3" class="form-step" style="display:none;">
                        
                        <div class="payment-box" id="dynamic-payment-box">
                            <h4>مبلغ قابل پرداخت حق عضویت</h4>
                            <p id="fee-text" style="font-weight:bold; color: #dc2626; font-size: 1.2rem;">لطفاً ابتدا در مرحله قبل وضعیت و مقطع تحصیلی خود را مشخص کنید.</p>
                            <div class="card-number">۵۸۵۹ - ۸۳۷۰ - ۲۴۲۶ - ۵۵۳۶</div>
                            <p style="color:#0c4a6e;">بانک تجارت | به نام: انجمن علمی مدیریت پسماند ایران</p>
                        </div>

                        <div class="input-group">
                            <label>آپلود تصویر فیش واریزی (حداکثر ۲ مگابایت) *</label>
                            <input type="file" name="فیش_واریزی" class="input-control" accept="image/*,.pdf" required>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                            <div class="input-group">
                                <label>تصویر کارت ملی (حداکثر ۲ مگابایت) *</label>
                                <input type="file" name="تصویر_کارت_ملی" class="input-control" accept="image/*,.pdf" required>
                            </div>
                            <div class="input-group">
                                <label>عکس پرسنلی ۳×۴ (حداکثر ۲ مگابایت) *</label>
                                <input type="file" name="عکس_پرسنلی" class="input-control" accept="image/*" required>
                            </div>
                        </div>

                        <div id="ind-alert-error" class="alert-box alert-error"></div>
                        <div id="ind-alert-success" class="alert-box alert-success">فرم شما با موفقیت ارسال شد. نتیجه ثبت‌نام به زودی اطلاع‌رسانی خواهد شد.</div>

                        <div class="btn-group">
                            <button type="button" class="btn btn-prev" onclick="prevStep('ind', 3)">&rarr; مرحله قبلی</button>
                            <button type="submit" id="ind-submit-btn" class="btn btn-submit">ارسال مدارک و درخواست عضویت</button>
                        </div>
                    </div>
                </form>
            </div>

            <div id="tab-corporate" class="tab-content">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: #104e8b; margin: 0 0 10px;">عضویت حقوقی (سازمان‌ها و شرکت‌ها)</h2>
                    <p style="color: #64748b; margin:0;">بهره‌مندی از ظرفیت‌های علمی، پژوهشی و شبکه‌سازی تخصصی</p>
                </div>

                <form id="corp-form" enctype="multipart/form-data">
                    <input type="hidden" name="access_key" value="0ddc649f-6c8e-4e32-810e-cb92ea65f7bf">
                    <input type="hidden" name="subject" value="درخواست عضویت حقوقی شرکت">
                    
                    <div class="payment-box" style="border-color: #104e8b; background: #f0f9ff;">
                        <h4 style="color: #104e8b;">حق عضویت سالیانه حقوقی</h4>
                        <p style="font-size: 1.4rem; font-weight: 900; color: #0c4a6e;">۵۰,۰۰۰,۰۰۰ ریال</p>
                        <div class="card-number">۵۸۵۹ - ۸۳۷۰ - ۲۴۲۶ - ۵۵۳۶</div>
                        <p style="color:#0c4a6e;">بانک تجارت | به نام: انجمن علمی مدیریت پسماند ایران</p>
                    </div>

                    <h3 style="color: #104e8b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px;">مشخصات ثبتی شرکت</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div class="input-group"><label>نام کامل شرکت *</label><input type="text" name="نام_شرکت" class="input-control" required></div>
                        <div class="input-group"><label>نوع شرکت *</label><select name="نوع_شرکت" class="input-control" required><option value="سهامی خاص">سهامی خاص</option><option value="سهامی عام">سهامی عام</option><option value="مسئولیت محدود">مسئولیت محدود</option><option value="سایر">سایر</option></select></div>
                        <div class="input-group"><label>نام مدیرعامل *</label><input type="text" name="مدیرعامل" class="input-control" required></div>
                        <div class="input-group"><label>حوزه فعالیت *</label><input type="text" name="حوزه_فعالیت" class="input-control" required></div>
                        <div class="input-group"><label>تاریخ آخرین آگهی روزنامه رسمی *</label><input type="text" name="تاریخ_آگهی" class="input-control" placeholder="مثال: ۱۴۰۲/۰۵/۱۲" required oninput="formatNationalId(this)"></div>
                        <div class="input-group"><label>آپلود آگهی روزنامه رسمی (حداکثر ۲ مگابایت) *</label><input type="file" name="فایل_روزنامه" class="input-control" accept=".pdf,image/*" required></div>
                    </div>

                    <h3 style="color: #104e8b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px; margin-top: 20px;">اطلاعات تماس و رابط</h3>
                    <div class="input-group"><label>آدرس دقیق پستی *</label><input type="text" name="آدرس" class="input-control" required></div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div class="input-group"><label>کد پستی *</label><input type="text" name="کدپستی" class="input-control" required oninput="formatNationalId(this)"></div>
                        <div class="input-group"><label>تلفن ثابت شرکت *</label><input type="text" name="تلفن_شرکت" class="input-control" dir="ltr" style="text-align:left;" required oninput="formatMobile(this)"></div>
                        <div class="input-group"><label>نام و نام خانوادگی رابط *</label><input type="text" name="نام_رابط" class="input-control" required oninput="validatePersian(this)"></div>
                        
                        <div class="input-group">
                            <label>شماره همراه رابط *</label>
                            <div class="mobile-wrapper">
                                <div class="country-select-container">
                                    <span id="flag-corp" class="fi fi-ir"></span>
                                    <select name="کد_کشور" onchange="document.getElementById('flag-corp').className = 'fi fi-' + this.options[this.selectedIndex].getAttribute('data-cc')">
                                        <option value="+98" data-cc="ir">ایران (+۹۸)</option>
                                        <option value="+1" data-cc="us">آمریکا (+۱)</option>
                                        <option value="+1" data-cc="ca">کانادا (+۱)</option>
                                        <option value="+44" data-cc="gb">انگلیس (+۴۴)</option>
                                        <option value="+49" data-cc="de">آلمان (+۴۹)</option>
                                        <option value="+33" data-cc="fr">فرانسه (+۳۳)</option>
                                        <option value="+90" data-cc="tr">ترکیه (+۹۰)</option>
                                        <option value="+971" data-cc="ae">امارات (+۹۷۱)</option>
                                        <option value="+964" data-cc="iq">عراق (+۹۶۴)</option>
                                        <option value="+61" data-cc="au">استرالیا (+۶۱)</option>
                                    </select>
                                </div>
                                <input type="text" name="موبایل_رابط" class="input-control mobile-input" required placeholder="۹۱۲۰۵۴۳۵۸۷" oninput="formatMobile(this)">
                            </div>
                        </div>

                        <div class="input-group"><label>ایمیل رابط *</label><input type="email" name="ایمیل_رابط" class="input-control" dir="ltr" style="text-align:left;" required></div>
                        <div class="input-group"><label>آپلود فیش واریزی (حداکثر ۲ مگابایت) *</label><input type="file" name="فیش_واریزی_حقوقی" class="input-control" accept=".pdf,image/*" required></div>
                    </div>

                    <div id="corp-alert-error" class="alert-box alert-error"></div>
                    <div id="corp-alert-success" class="alert-box alert-success">درخواست حقوقی شما با موفقیت ثبت شد. جهت هماهنگی تماس گرفته خواهد شد.</div>

                    <div class="btn-group" style="justify-content: center; margin-top: 20px;">
                        <button type="submit" id="corp-submit-btn" class="btn btn-submit" style="width: 100%; max-width: 400px; background: #104e8b;">ثبت‌نام حقوقی و ارسال مدارک</button>
                    </div>
                </form>
            </div>

            <div id="tab-status" class="tab-content">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: var(--color-dark); margin: 0 0 10px;">استعلام وضعیت ثبت‌نام و کارت عضویت</h2>
                    <p style="color: #64748b; margin:0;">کد ملی و شماره موبایل خود را جهت مشاهده آخرین وضعیت وارد کنید.</p>
                </div>

                <div style="background: #f8fafc; padding: 30px; border-radius: 16px; border: 1px solid #e2e8f0; max-width: 500px; margin: 0 auto;">
                    <div class="input-group">
                        <label>کد ملی (۱۰ رقم)</label>
                        <input type="text" id="check_nid" class="input-control" maxlength="10" placeholder="۰۰۱۲۳۴۵۶۷۸" oninput="formatNationalId(this)">
                    </div>
                    <div class="input-group">
                        <label>شماره موبایل ثبت نامی</label>
                        <input type="text" id="check_phone" class="input-control" dir="ltr" style="text-align:left;" placeholder="۹۱۲۰۵۴۳۵۸۷" oninput="formatMobile(this)">
                    </div>
                    <button type="button" class="btn btn-submit" style="width: 100%;" onclick="checkMembershipStatus()">بررسی وضعیت من</button>
                    <div id="loading-status" class="loading-spinner">در حال ارتباط با سرور امن انجمن...</div>
                </div>

                <div id="status-result" class="status-card">
                    <h3 style="text-align: center; color: var(--color-primary); margin-top:0;">نتیجه استعلام</h3>
                    <div class="status-grid">
                        <div class="status-item"><span>نام و نام خانوادگی:</span><strong id="res_name">-</strong></div>
                        <div class="status-item"><span>شماره عضویت:</span><strong id="res_id">-</strong></div>
                        <div class="status-item"><span>نوع عضویت:</span><strong id="res_type">-</strong></div>
                        <div class="status-item"><span>مقطع تحصیلی:</span><strong id="res_edu">-</strong></div>
                        <div class="status-item"><span>وضعیت عکس پرسنلی:</span><strong id="res_pic">-</strong></div>
                        <div class="status-item"><span>زمان باقی‌مانده اعتبار (روز):</span><strong id="res_time" style="color:#ea580c;">-</strong></div>
                    </div>
                    <div style="margin-top: 20px; background: #e0f2fe; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #bae6fd;">
                        <span style="display: block; color: #0369a1; font-size: 0.9rem; margin-bottom: 5px;">وضعیت صدور کارت عضویت:</span>
                        <strong id="res_card" style="font-size: 1.4rem; color: #0c4a6e; font-weight: 900;">-</strong>
                    </div>
                </div>
                
                <div id="status-error" style="display:none; background: #fef2f2; color: #991b1b; padding: 20px; border-radius: 12px; border: 1px solid #fecaca; text-align: center; margin-top: 30px; max-width: 500px; margin-left: auto; margin-right: auto;">
                    اطلاعاتی با این کد ملی و شماره موبایل یافت نشد. لطفاً از صحت اطلاعات وارد شده اطمینان حاصل کنید.
                </div>
            </div>

        </div>
    </section>

    <script>
        // --- Tab Switching Logic ---
        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabId).classList.add('active');
        }

        // --- Multi-Step Form Logic ---
        function nextStep(formType, current) {
            document.getElementById(`${formType}-step-${current}`).style.display = 'none';
            document.getElementById(`${formType}-step-${current + 1}`).style.display = 'block';
        }
        function prevStep(formType, current) {
            document.getElementById(`${formType}-step-${current}`).style.display = 'none';
            document.getElementById(`${formType}-step-${current - 1}`).style.display = 'block';
        }

        // --- Validation & Persian Digits Formatting Logic ---
        const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
        const englishDigits = '0123456789';

        function toEnglishDigits(str) {
            if (!str) return '';
            return str.toString().replace(/[۰-۹]/g, w => englishDigits[persianDigits.indexOf(w)]);
        }
        function toPersianDigits(str) {
            if (!str) return '';
            return str.toString().replace(/\d/g, d => persianDigits[d]);
        }

        function formatNationalId(input) {
            let val = toEnglishDigits(input.value);
            val = val.replace(/[^0-9]/g, ''); 
            input.value = toPersianDigits(val);
        }

        function formatMobile(input) {
            let val = toEnglishDigits(input.value);
            val = val.replace(/[^0-9]/g, ''); 
            if(val.length === 11 && val.startsWith('0')) { val = val.substring(1); }
            if(val.length > 10) val = val.slice(0, 10);
            input.value = toPersianDigits(val);
        }

        function validatePersian(input) {
            input.value = input.value.replace(/[^\u0600-\u06FF\\s]/g, '');
        }

        // --- Student Status & Dynamic Auto-fill Logic ---
        function handleStudentStatus() {
            const status = document.getElementById('edu_status').value;
            const studentFields = document.getElementById('student-fields');
            const gradFields = document.getElementById('grad-fields');
            const feeText = document.getElementById('fee-text');
            const paymentBox = document.getElementById('dynamic-payment-box');
            
            const studentSelect = document.getElementById('student_level');
            const studentCard = document.getElementById('student_card_img');
            const gradSelect = document.getElementById('grad_level');
            const jobInput = document.getElementById('job_title_input'); // Target for auto-fill

            if(status === 'دانشجو') {
                studentFields.style.display = 'block';
                gradFields.style.display = 'none';
                studentSelect.setAttribute('required', 'true');
                studentCard.setAttribute('required', 'true');
                gradSelect.removeAttribute('required');
                
                // Auto-fill Job as "دانشجو"
                jobInput.value = 'دانشجو';
                
                paymentBox.style.borderColor = '#eab308';
                feeText.innerHTML = `مبلغ قابل پرداخت (حق عضویت دانشجویی): ${toPersianDigits('500,000')} ریال`;
                feeText.style.color = '#ca8a04';

            } else if(status === 'فارغ التحصیل') {
                studentFields.style.display = 'none';
                gradFields.style.display = 'block';
                studentSelect.removeAttribute('required');
                studentCard.removeAttribute('required');
                gradSelect.setAttribute('required', 'true');

                // Clear the auto-filled "دانشجو" if they switch to Graduated
                if(jobInput.value === 'دانشجو') {
                    jobInput.value = '';
                }

                const level = gradSelect.value;
                if(level === 'کارشناسی ارشد' || level === 'دکتری تخصصی') {
                    paymentBox.style.borderColor = '#16a34a';
                    feeText.innerHTML = `مبلغ قابل پرداخت (عضویت پیوسته): ${toPersianDigits('2,500,000')} ریال`;
                    feeText.style.color = '#15803d';
                } else if(level === 'دیپلم' || level === 'کاردانی' || level === 'کارشناسی') {
                    paymentBox.style.borderColor = '#0284c7';
                    feeText.innerHTML = `مبلغ قابل پرداخت (عضویت وابسته): ${toPersianDigits('1,500,000')} ریال`;
                    feeText.style.color = '#0369a1';
                } else {
                    paymentBox.style.borderColor = '#ef4444';
                    feeText.innerHTML = 'لطفاً مقطع تحصیلی خود را جهت محاسبه دقیق حق عضویت انتخاب کنید.';
                    feeText.style.color = '#b91c1c';
                }
            }
        }

        // --- AJAX Form Submission ---
        function setupAjaxForm(formId, btnId, errId, sucId) {
            const form = document.getElementById(formId);
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const errBox = document.getElementById(errId);
                const sucBox = document.getElementById(sucId);
                const submitBtn = document.getElementById(btnId);
                errBox.style.display = 'none';
                sucBox.style.display = 'none';

                // File Size Validation (Max 2MB per file)
                const fileInputs = form.querySelectorAll('input[type="file"]');
                const maxSize = 2 * 1024 * 1024; // 2MB
                for (let fileInput of fileInputs) {
                    if (fileInput.files.length > 0 && fileInput.files[0].size > maxSize) {
                        errBox.innerText = 'خطا: حجم فایل انتخابی بیشتر از ۲ مگابایت است. لطفاً فایل کم‌حجم‌تری انتخاب کنید.';
                        errBox.style.display = 'block';
                        return;
                    }
                }

                const formData = new FormData(form);
                
                // UX: Show loading spinner
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="4.93" x2="19.07" y2="7.76"></line></svg> در حال ارسال...';
                
                if(!document.getElementById('spin-anim')) {
                    const style = document.createElement('style');
                    style.id = 'spin-anim';
                    style.innerHTML = `@keyframes spin { 100% { transform: rotate(360deg); } }`;
                    document.head.appendChild(style);
                }

                fetch('https://api.web3forms.com/submit', {
                    method: 'POST',
                    body: formData
                })
                .then(async (response) => {
                    let json = await response.json();
                    if (response.status == 200) {
                        sucBox.style.display = 'block';
                        form.reset();
                        if(formId === 'ind-form') {
                            document.getElementById('student-fields').style.display = 'none';
                            document.getElementById('grad-fields').style.display = 'none';
                            document.getElementById('fee-text').innerHTML = 'لطفاً ابتدا در مرحله قبل وضعیت و مقطع تحصیلی خود را مشخص کنید.';
                            document.getElementById('dynamic-payment-box').style.borderColor = '#0284c7';
                        }
                    } else {
                        errBox.innerText = json.message || "خطا در ارسال فرم. لطفاً مجدداً تلاش کنید.";
                        errBox.style.display = 'block';
                    }
                })
                .catch(error => {
                    errBox.innerText = "ارتباط با سرور برقرار نشد. لطفاً اینترنت خود را بررسی کنید.";
                    errBox.style.display = 'block';
                })
                .finally(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'ارسال مدارک و درخواست عضویت';
                });
            });
        }

        setupAjaxForm('ind-form', 'ind-submit-btn', 'ind-alert-error', 'ind-alert-success');
        setupAjaxForm('corp-form', 'corp-submit-btn', 'corp-alert-error', 'corp-alert-success');


        // --- Secure Apps Script Fetch Logic ---
        async function checkMembershipStatus() {
            let nid_fa = document.getElementById('check_nid').value;
            let phone_fa = document.getElementById('check_phone').value;
            
            let nid = toEnglishDigits(nid_fa);
            let phone = toEnglishDigits(phone_fa);
            
            if(nid.length < 10 || phone.length < 10) {
                alert("لطفاً کد ملی و شماره موبایل را به صورت کامل وارد کنید.");
                return;
            }

            if(phone.length === 11 && phone.startsWith('0')) phone = phone.substring(1);

            document.getElementById('loading-status').style.display = 'block';
            document.getElementById('status-result').style.display = 'none';
            document.getElementById('status-error').style.display = 'none';

            // YOUR SECURE GOOGLE APPS SCRIPT WEB APP URL
            const scriptUrl = 'https://script.google.com/macros/s/AKfycbxRRkJURuqzYKdUFwrgHM09NGGkgVo7j75GXNoy-ntXMMNcmPvaCwxRzwJfj0Q32BnE/exec';
            
            const fetchUrl = `${scriptUrl}?nid=${encodeURIComponent(nid)}&phone=${encodeURIComponent(phone)}`;

            try {
                const response = await fetch(fetchUrl);
                const result = await response.json();

                if(result.status === "success") {
                    document.getElementById('res_id').innerText = toPersianDigits(result.data.id);
                    document.getElementById('res_name').innerText = toPersianDigits(result.data.name);
                    document.getElementById('res_pic').innerText = toPersianDigits(result.data.pic);
                    document.getElementById('res_type').innerText = toPersianDigits(result.data.type);
                    document.getElementById('res_edu').innerText = toPersianDigits(result.data.edu);
                    document.getElementById('res_card').innerText = toPersianDigits(result.data.card);
                    document.getElementById('res_time').innerText = toPersianDigits(result.data.time);
                    
                    document.getElementById('loading-status').style.display = 'none';
                    document.getElementById('status-result').style.display = 'block';
                } else {
                    document.getElementById('loading-status').style.display = 'none';
                    document.getElementById('status-error').style.display = 'block';
                }
            } catch (error) {
                console.error("Error fetching data:", error);
                document.getElementById('loading-status').style.display = 'none';
                alert("خطا در ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید.");
            }
        }
    </script>
    """

    final_membership_page = master_template.replace("{{ include 'components/header.html' }}", header)
    final_membership_page = final_membership_page.replace("{{ include 'components/footer.html' }}", footer)
    final_membership_page = final_membership_page.replace("{{ content }}", membership_page_html)
    final_membership_page = final_membership_page.replace("{{ title }}", "پورتال عضویت و استعلام")

    with open(os.path.join(base_dir, 'membership.html'), 'w', encoding='utf-8') as f:
        f.write(final_membership_page)
        
    print("Boom! Index, Article pages, AND Search page generated successfully!")

if __name__ == "__main__":
    build_site()