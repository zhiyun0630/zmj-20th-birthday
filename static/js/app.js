(function () {
    'use strict';

    const CONFIG = window.SITE_CONFIG || {};

    // ========== 工具函数 ==========
    function $(id) { return document.getElementById(id); }

    function showToast(msg) {
        const toast = $('toast');
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2500);
    }

    function daysTogether(since) {
        const start = new Date(since);
        const now = new Date();
        const diff = now - start;
        return Math.floor(diff / (1000 * 60 * 60 * 24));
    }

    // ========== 星星背景 ==========
    function createStars() {
        const container = $('stars');
        if (!container) return;
        const count = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 15 : 50;
        for (let i = 0; i < count; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            const size = Math.random() * 4 + 3;
            star.style.cssText = `
                left:${Math.random() * 100}%;
                top:${Math.random() * 100}%;
                width:${size}px;height:${size}px;
                animation-delay:${Math.random() * 6}s;
            `;
            container.appendChild(star);
        }
    }

    // ========== 飘落花瓣 ==========
    function createPetals() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        const emojis = ['🌸', '💗', '✨', '🩷'];
        setInterval(() => {
            const petal = document.createElement('div');
            petal.className = 'petal';
            petal.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            petal.style.cssText = `
                left:${Math.random() * 100}%;
                font-size:${Math.random() * 10 + 12}px;
                animation-duration:${Math.random() * 4 + 6}s;
            `;
            document.body.appendChild(petal);
            petal.addEventListener('animationend', () => petal.remove());
        }, 1200);
    }

    // ========== 滚动显现 ==========
    function initReveal() {
        const els = document.querySelectorAll('.reveal');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.classList.add('visible');
                    observer.unobserve(e.target);
                }
            });
        }, { threshold: 0.15 });
        els.forEach(el => observer.observe(el));
    }

    // ========== 在一起天数 ==========
    function initDaysCounter() {
        const el = $('daysCounter');
        if (!el || !CONFIG.together_since) return;
        el.textContent = daysTogether(CONFIG.together_since);
    }

    // ========== 时间线 ==========
    function initTimeline() {
        const items = document.querySelectorAll('.timeline-item');
        const detail = $('timelineDetail');
        if (!items.length || !detail) return;

        items.forEach((item, i) => {
            item.addEventListener('click', () => {
                items.forEach(t => t.classList.remove('active'));
                item.classList.add('active');
                const events = CONFIG.timeline || [];
                detail.textContent = events[i]?.detail || events[i]?.text || '';
            });
        });

        if (items[0]) {
            items[0].classList.add('active');
            const first = (CONFIG.timeline || [])[0];
            detail.textContent = first?.detail || first?.text || '';
        }
    }

    // ========== 信封 ==========
    let envelopeOpened = false;

    function openEnvelope() {
        if (envelopeOpened) return;
        envelopeOpened = true;

        $('envelope').classList.add('opened');

        setTimeout(() => {
            $('envelopeWrap').classList.add('hide');
            $('mainContent').style.opacity = '1';
            $('musicBtn').classList.add('visible');
            tryPlayMusic();
        }, 800);
    }

    // ========== 音乐 ==========
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
            showToast('可以在 config.json 里添加背景音乐 ♪');
            return;
        }
        if (musicPlaying) {
            audio.pause();
            musicPlaying = false;
        } else {
            audio.volume = 0.25;
            audio.play().catch(() => showToast('点击页面后再试一次 ♪'));
            musicPlaying = true;
        }
        updateMusicBtn();
    }

    function updateMusicBtn() {
        const btn = $('musicBtn');
        btn.textContent = musicPlaying ? '🔊' : '🔇';
        btn.classList.toggle('playing', musicPlaying);
        btn.setAttribute('aria-label', musicPlaying ? '关闭音乐' : '播放音乐');
    }

    // ========== 吹蜡烛 ==========
    let blownCount = 0;
    let totalCandles = 0;

    function blowCandle(candle) {
        if (candle.classList.contains('blown')) return;
        candle.classList.add('blown');
        blownCount++;
        $('candleCount').textContent = totalCandles - blownCount;

        if (blownCount === totalCandles) {
            $('candleTip').textContent = '生日快乐！🎂 愿望一定会实现的';
            launchConfetti();
            playBirthdaySong();
        }
    }

    function launchConfetti() {
        if (typeof confetti !== 'function') return;
        const colors = ['#ff6b9d', '#ffd700', '#fff', '#ff8fab'];
        confetti({ particleCount: 150, angle: 60, spread: 80, origin: { x: 0 }, colors });
        confetti({ particleCount: 150, angle: 120, spread: 80, origin: { x: 1 }, colors });
        setTimeout(() => confetti({ particleCount: 200, spread: 160, origin: { y: 0.6 }, colors }), 500);
    }

    function playBirthdaySong() {
        if (!CONFIG.birthday_song) return;
        const audio = new Audio(CONFIG.birthday_song);
        audio.volume = 0.4;
        audio.play().catch(() => {});
    }

    // ========== 打字机 ==========
    let typingStarted = false;

    function typeWriter() {
        if (typingStarted) return;
        typingStarted = true;

        const text = CONFIG.letter || '';
        const typedEl = $('typedText');
        const cursor = $('cursor');
        let i = 0;

        function type() {
            if (i < text.length) {
                typedEl.textContent = text.substring(0, i + 1);
                i++;
                setTimeout(type, text[i - 1] === '\n' ? 280 : 45);
            } else if (cursor) {
                cursor.style.display = 'none';
            }
        }
        type();
    }

    function initTypeWriter() {
        const section = document.querySelector('.letter-section');
        if (!section) return;
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                typeWriter();
                observer.disconnect();
            }
        }, { threshold: 0.3 });
        observer.observe(section);
    }

    // ========== 彩蛋 ==========
    function checkSecret() {
        const input = $('secretInput').value.trim();
        if (input === CONFIG.secret_code) {
            $('secretReveal').classList.add('show');
            launchConfetti();
        } else {
            showToast('暗号不对哦，再想想~ 💭');
            $('secretInput').classList.add('shake');
            setTimeout(() => $('secretInput').classList.remove('shake'), 500);
        }
    }

    // ========== 初始化 ==========
    function init() {
        createStars();
        createPetals();
        initReveal();
        initDaysCounter();
        initTimeline();
        initTypeWriter();

        totalCandles = document.querySelectorAll('.candle').length;
        if ($('candleCount')) $('candleCount').textContent = totalCandles;

        $('envelope').addEventListener('click', openEnvelope);
        $('musicBtn').addEventListener('click', toggleMusic);
        $('secretBtn').addEventListener('click', checkSecret);
        $('secretInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') checkSecret();
        });

        document.querySelectorAll('.candle').forEach(c => {
            c.addEventListener('click', () => blowCandle(c));
        });

        document.querySelectorAll('.gift-box').forEach(box => {
            box.addEventListener('click', () => box.classList.toggle('opened'));
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
