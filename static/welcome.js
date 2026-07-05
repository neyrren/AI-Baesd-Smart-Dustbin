let current = 0;
const slides = document.querySelectorAll('.slide-full');
const dots   = document.querySelectorAll('.dot');
let timer;

function goTo(n) {
  slides[current].classList.remove('active');
  dots[current].classList.remove('active');
  current = (n + slides.length) % slides.length;
  slides[current].classList.add('active');
  dots[current].classList.add('active');
  resetTimer();
}

function changeSlide(dir) { goTo(current + dir); }

function resetTimer() {
  clearInterval(timer);
  timer = setInterval(() => goTo(current + 1), 6000);
}

// Start auto-advance
resetTimer();