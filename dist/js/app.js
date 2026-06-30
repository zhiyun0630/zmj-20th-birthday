(function () {
    'use strict';

    const CONFIG = window.SITE_CONFIG || {};
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function $(id) { return document.getElementById(id); }

    function showToast(message) {
        const toast = $('toast');
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add('show');
        window.clearTimeout(showToast.timer);
        showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2600);
    }

    function daysTogether(since) {
        const start = new Date(`${since}T00:00:00`);
        const today = new Date();
        const current = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        return Math.max(0, Math.floor((current - start) / 86400000) + 1);
    }

    function launchConfetti(intense) {
        if (typeof confetti !== 'function') return;
        const colors = ['#ff5f9e', '#ff7eb3', '#ffd166', '#ffffff', '#ff9a8b'];
        const count = intense ? 220 : 120;
        confetti({ particleCount: count, spread: 90, origin: { x: 0.18, y: 0.68 }, colors });
        confetti({ particleCount: count, spread: 90, origin: { x: 0.82, y: 0.68 }, colors });
        window.setTimeout(() => confetti({ particleCount: intense ? 260 : 140, spread: 160, startVelocity: 38, origin: { y: 0.58 }, colors }), 260);
    }

    function initSparkCanvas() {
        const canvas = $('sparkCanvas');
        if (!canvas || reduceMotion) return;
        const ctx = canvas.getContext('2d');
        const sparks = [];
        const total = Math.min(120, Math.floor(window.innerWidth / 10));
        let width = 0;
        let height = 0;

        function resize() {
            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            canvas.style.width = `${width}px`;
            canvas.style.height = `${height}px`;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }

        function createSpark() {
            return {
                x: Math.random() * width,
                y: Math.random() * height,
                r: Math.random() * 1.9 + 0.7,
                vx: (Math.random() - 0.5) * 0.25,
                vy: Math.random() * 0.28 + 0.08,
                alpha: Math.random() * 0.55 + 0.25,
                twinkle: Math.random() * Math.PI * 2
            };
        }

        function draw() {
            ctx.clearRect(0, 0, width, height);
            sparks.forEach((spark) => {
                spark.x += spark.vx;
                spark.y += spark.vy;
                spark.twinkle += 0.035;
                if (spark.y > height + 10) {
                    Object.assign(spark, createSpark(), { y: -10 });
                }
                const alpha = spark.alpha * (0.65 + Math.sin(spark.twinkle) * 0.35);
                ctx.beginPath();
                ctx.fillStyle = `rgba(255,255,255,${alpha})`;
                ctx.shadowColor = 'rgba(255,126,179,0.75)';
                ctx.shadowBlur = 12;
                ctx.arc(spark.x, spark.y, spark.r, 0, Math.PI * 2);
                ctx.fill();
            });
            requestAnimationFrame(draw);
        }

        resize();
        for (let i = 0; i < total; i++) sparks.push(createSpark());
        window.addEventListener('resize', resize);
        draw();
    }

    function initFloatingHearts() {
        const container = $('floatingHearts');
        if (!container || reduceMotion) return;
        const symbols = ['♡', '✦', '✧', '❤', '❀'];
        window.setInterval(() => {
            const heart = document.createElement('span');
            heart.className = 'heart';
            heart.textContent = symbols[Math.floor(Math.random() * symbols.length)];
            heart.style.left = `${Math.random() * 100}%`;
            heart.style.fontSize = `${Math.random() * 18 + 14}px`;
            heart.style.opacity = `${Math.random() * 0.45 + 0.35}`;
            heart.style.setProperty('--drift', `${(Math.random() - 0.5) * 160}px`);
            heart.style.animationDuration = `${Math.random() * 5 + 7}s`;
            container.appendChild(heart);
            heart.addEventListener('animationend', () => heart.remove());
        }, 760);
    }

    function initReveal() {
        const els = document.querySelectorAll('.reveal');
        if (!('IntersectionObserver' in window)) {
            els.forEach(el => el.classList.add('visible'));
            return;
        }
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.16 });
        els.forEach((el, index) => {
            el.style.transitionDelay = `${Math.min(index % 4, 3) * 0.08}s`;
            observer.observe(el);
        });
    }

    function initDaysCounter() {
        const el = $('daysCounter');
        if (!el || !CONFIG.together_since) return;
        const target = daysTogether(CONFIG.together_since);
        if (reduceMotion) {
            el.textContent = target;
            return;
        }
        const duration = 1300;
        const start = performance.now();
        function tick(now) {
            const progress = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(target * eased);
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    function initTimeline() {
        const items = Array.from(document.querySelectorAll('.timeline-item'));
        const detail = $('timelineDetail');
        if (!items.length || !detail) return;

        function activate(index) {
            items.forEach(item => item.classList.remove('active'));
            items[index].classList.add('active');
            const event = (CONFIG.timeline || [])[index] || {};
            detail.style.opacity = '0';
            window.setTimeout(() => {
                detail.textContent = event.detail || event.text || '';
                detail.style.opacity = '1';
            }, 140);
        }

        items.forEach((item, index) => item.addEventListener('click', () => activate(index)));
        activate(0);
    }

    function initIntro() {
        const openCard = $('openCard');
        const intro = $('intro');
        const main = $('mainContent');
        const musicBtn = $('musicBtn');
        if (!openCard || !intro || !main) return;

        openCard.addEventListener('click', () => {
            intro.classList.add('hide');
            main.classList.add('show');
            musicBtn?.classList.add('visible');
            launchConfetti(false);
            tryPlayMusic();
            window.setTimeout(() => intro.remove(), 1000);
        }, { once: true });
    }

    let musicPlaying = false;

    function tryPlayMusic() {
        const audio = $('bgMusic');
        if (!audio || !CONFIG.bg_music) return;
        audio.volume = 0.25;
        audio.play().then(() => {
            musicPlaying = true;
            updateMusicBtn();
        }).catch(() => {});
    }

    function toggleMusic() {
        const audio = $('bgMusic');
        if (!audio || !CONFIG.bg_music) {
            showToast('把音乐放到 assets/music，并在 config.json 里填写路径就能播放啦');
            return;
        }
        if (musicPlaying) {
            audio.pause();
            musicPlaying = false;
        } else {
            audio.volume = 0.25;
            audio.play().then(() => { musicPlaying = true; updateMusicBtn(); }).catch(() => showToast('再点击页面一次试试播放音乐'));
            return;
        }
        updateMusicBtn();
    }

    function updateMusicBtn() {
        const btn = $('musicBtn');
        if (!btn) return;
        btn.textContent = musicPlaying ? '🔊' : '🔇';
        btn.classList.toggle('playing', musicPlaying);
        btn.setAttribute('aria-label', musicPlaying ? '关闭音乐' : '播放音乐');
    }

    function initGallery() {
        const stage = $('photoStage');
        const prev = $('photoPrev');
        const next = $('photoNext');
        const dots = $('photoDots');
        if (!stage) return;
        const cards = Array.from(stage.querySelectorAll('.photo-card'));
        if (!cards.length) return;

        function cardWidth() {
            const first = cards[0];
            const gap = parseFloat(getComputedStyle(stage).gap || '0');
            return first.getBoundingClientRect().width + gap;
        }

        function scrollByCard(direction) {
            stage.scrollBy({ left: cardWidth() * direction, behavior: 'smooth' });
        }

        function updateDots() {
            if (!dots) return;
            const index = Math.round(stage.scrollLeft / cardWidth());
            dots.querySelectorAll('.photo-dot').forEach((dot, dotIndex) => dot.classList.toggle('active', dotIndex === index));
        }

        if (dots) {
            cards.forEach((_, index) => {
                const dot = document.createElement('button');
                dot.className = `photo-dot${index === 0 ? ' active' : ''}`;
                dot.setAttribute('aria-label', `查看第 ${index + 1} 张照片`);
                dot.addEventListener('click', () => stage.scrollTo({ left: cardWidth() * index, behavior: 'smooth' }));
                dots.appendChild(dot);
            });
        }

        prev?.addEventListener('click', () => scrollByCard(-1));
        next?.addEventListener('click', () => scrollByCard(1));
        stage.addEventListener('scroll', () => window.requestAnimationFrame(updateDots), { passive: true });
    }

    let cakeDone = false;

    function blowAllCandles() {
        if (cakeDone) return;
        cakeDone = true;
        const candles = Array.from(document.querySelectorAll('.candle'));
        const tip = $('candleTip');
        const count = $('candleCount');
        const button = $('blowAllBtn');
        const wishCloud = $('wishCloud');

        candles.forEach((candle, index) => {
            window.setTimeout(() => candle.classList.add('blown'), index * 38);
        });
        if (count) count.textContent = '0';
        if (button) {
            button.textContent = '愿望已送达星星那里';
            button.disabled = true;
        }
        window.setTimeout(() => {
            if (tip) tip.textContent = '生日快乐！愿敏君的愿望全部实现。';
            if (wishCloud) wishCloud.textContent = '二十岁的敏君，万事胜意，岁岁欢喜';
            launchConfetti(true);
            playBirthdaySong();
            showToast('一口气吹灭啦，愿望一定会实现');
        }, candles.length * 38 + 180);
    }

    function playBirthdaySong() {
        if (!CONFIG.birthday_song) return;
        const audio = new Audio(CONFIG.birthday_song);
        audio.volume = 0.42;
        audio.play().catch(() => {});
    }

    let typingStarted = false;

    function typeWriter() {
        if (typingStarted) return;
        typingStarted = true;
        const text = CONFIG.letter || '';
        const typedEl = $('typedText');
        const cursor = $('cursor');
        if (!typedEl) return;
        let index = 0;
        function type() {
            typedEl.textContent = text.slice(0, index + 1);
            index++;
            if (index < text.length) {
                const prev = text[index - 1];
                window.setTimeout(type, prev === '\n' ? 260 : 42);
            } else if (cursor) {
                cursor.style.display = 'none';
            }
        }
        type();
    }

    function initTypeWriter() {
        const section = $('letter');
        if (!section) return;
        if (!('IntersectionObserver' in window)) {
            typeWriter();
            return;
        }
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                typeWriter();
                observer.disconnect();
            }
        }, { threshold: 0.32 });
        observer.observe(section);
    }

    function initSecret() {
        const input = $('secretInput');
        const btn = $('secretBtn');
        const reveal = $('secretReveal');
        if (!input || !btn || !reveal) return;

        function checkSecret() {
            const normalized = input.value.trim().replace(/[.\-/\s年月日]/g, '');
            const code = String(CONFIG.secret_code || '').replace(/[.\-/\s年月日]/g, '');
            if (normalized === code) {
                reveal.classList.add('show');
                launchConfetti(true);
                showToast('解锁成功，这是只属于敏君的惊喜');
            } else {
                showToast('暗号不对哦，提示：我们的相识日期');
                input.classList.add('shake');
                window.setTimeout(() => input.classList.remove('shake'), 450);
            }
        }

        btn.addEventListener('click', checkSecret);
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') checkSecret();
        });
    }

    function initGifts() {
        document.querySelectorAll('.gift-box').forEach((box) => {
            box.addEventListener('click', () => box.classList.toggle('opened'));
        });
    }

    function init() {
        initSparkCanvas();
        initFloatingHearts();
        initReveal();
        initDaysCounter();
        initTimeline();
        initIntro();
        initGallery();
        initTypeWriter();
        initSecret();
        initGifts();

        $('musicBtn')?.addEventListener('click', toggleMusic);
        $('surpriseBtn')?.addEventListener('click', () => launchConfetti(true));
        $('blowAllBtn')?.addEventListener('click', blowAllCandles);

        const count = document.querySelectorAll('.candle').length;
        if ($('candleCount')) $('candleCount').textContent = count;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
