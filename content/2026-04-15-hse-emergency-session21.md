---
title: "جلسه بیستم: مدیریت بهداشت و محیط زیست در شرایط اضطراری"
date: "2026-04-15"
image: "./assets/images/news/hse-emergency-session21.jpg"
tags: ["دوره‌ها و کارگاه‌ها", "اخبار"]
---

<div id="course-status-badge" style="padding: 8px 20px; border-radius: 50px; display: inline-block; font-weight: bold; margin-bottom: 30px; border: 1px solid #cbd5e1; font-size: 1rem; transition: all 0.3s ease;">
    در حال بررسی وضعیت زمان برگزاری...
</div>

<p style="font-size: 1.1rem; line-height: 2; text-align: justify;">
شرکت مدیریت پسماند شیمی کشاورز با همکاری انجمن علمی مهندسی و مدیریت پسماند ایران، در راستای صیانت از محیط زیست و پاسخی ملی به چالش‌های جهانی، <strong>جلسه بیستم و یکم</strong> از سلسله دوره‌های آموزشی مدیریت پسماند را با موضوع <em>«مدیریت بهداشت و محیط زیست در شرایط اضطراری»</em> برگزار می‌کند.
</p>

<div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 25px; border-radius: 16px; margin: 35px 0; display: flex; align-items: center; gap: 20px;">
    <div>
        <span style="color: #15803d; font-size: 0.95rem; font-weight: bold; margin-bottom: 5px; display: block;">مدرس دوره:</span>
        <h4 style="margin: 0; color: #166534; font-size: 1.4rem; font-weight: 900;">دکتر علیرضا عسگری</h4>
    </div>
</div>

<h3 style="color: var(--color-primary); margin-top: 40px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; font-weight: 900; font-size: 1.4rem;">مشخصات برگزاری دوره</h3>
<ul style="font-size: 1.1rem; line-height: 2.2; list-style-type: square; padding-right: 20px; margin-bottom: 30px;">
    <li><strong>تاریخ برگزاری:</strong> چهارشنبه ۲۶ فروردین‌ماه ۱۴۰۵</li>
    <li><strong>زمان برگزاری:</strong> ساعت ۱۹:۰۰ الی ۲۱:۰۰</li>
    <li><strong>پلتفرم برگزاری:</strong> سامانه اسکای روم (مجازی)</li>
    <li><strong>شرایط حضور:</strong> رایگان و برای عموم آزاد است (برای اعضای انجمن گواهی صادر می‌شود)</li>
</ul>

<div style="background: #eff6ff; border: 1px dashed #bfdbfe; padding: 20px; border-radius: 12px; margin-top: 20px; display: flex; justify-content: space-around; flex-wrap: wrap;">
    <span style="color: #1d4ed8; font-weight: bold;">📞 تلفن تماس: ۰۲۱۲۲۹۰۰۶۵۷</span>
    <span style="color: #1d4ed8; font-weight: bold;">📱 پیامگیر: ۰۹۸۹۹۸۲۰۰۳۹۵۰</span>
</div>

<div style="text-align: center; margin-top: 50px; margin-bottom: 20px;">
    <a href="#" id="course-action-btn" style="display: inline-block; padding: 16px 50px; border-radius: 50px; font-weight: 900; font-size: 1.2rem; color: white; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        در حال بررسی...
    </a>
</div>

<script>
    function updateCourseStatus() {
        const now = new Date().getTime();
        
        // زمان شروع و پایان جلسه بیستم (26 فروردین 1405 معادل 15 آوریل 2026)
        const startTime = new Date('2026-04-15T19:00:00+03:30').getTime();
        const endTime = new Date('2026-04-15T21:00:00+03:30').getTime();

        const badge = document.getElementById('course-status-badge');
        const btn = document.getElementById('course-action-btn');

        if (now < startTime) {
            // حالت 1: قبل از شروع دوره
            badge.innerHTML = '⏳ وضعیت دوره: در انتظار برگزاری';
            badge.style.backgroundColor = '#fffbeb';
            badge.style.color = '#b45309';
            badge.style.borderColor = '#fde68a';

            btn.href = '#';
            btn.innerHTML = 'لینک ورود در زمان برگزاری فعال می‌شود';
            btn.style.backgroundColor = '#94a3b8';
            btn.style.cursor = 'not-allowed';
            btn.onclick = function(e) { e.preventDefault(); };

        } else if (now >= startTime && now <= endTime) {
            // حالت 2: دقیقاً در زمان برگزاری
            badge.innerHTML = '🟢 وضعیت دوره: در حال برگزاری';
            badge.style.backgroundColor = '#dcfce7';
            badge.style.color = '#166534';
            badge.style.borderColor = '#bbf7d0';

            btn.href = 'https://skyroom.online/ch/mellishimisabz/wmac-training';
            btn.innerHTML = 'ورود به دوره (اسکای‌روم) &larr;';
            btn.style.backgroundColor = '#16a34a';
            btn.style.cursor = 'pointer';
            btn.onclick = null;

        } else {
            // حالت 3: بعد از اتمام دوره
            badge.innerHTML = '✔️ وضعیت دوره: با موفقیت برگزار شد';
            badge.style.backgroundColor = '#f1f5f9';
            badge.style.color = '#475569';
            badge.style.borderColor = '#cbd5e1';

            btn.href = '#';
            btn.innerHTML = 'زمان این دوره پایان یافته است';
            btn.style.backgroundColor = '#64748b';
            btn.style.cursor = 'not-allowed';
            btn.onclick = function(e) { e.preventDefault(); };
        }
    }

    // اجرای تابع هنگام لود صفحه
    updateCourseStatus();
    // چک کردن زمان به صورت خودکار هر 1 دقیقه
    setInterval(updateCourseStatus, 60000);
</script>