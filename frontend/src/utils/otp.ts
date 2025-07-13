import { ref } from "vue";

export function useCountdown(initialSeconds: number = 60) {
  const countdown = ref(initialSeconds);
  const canResend = ref(false);
  let countdownInterval: number | undefined;

  function startCountdown(seconds: number = initialSeconds) {
    countdown.value = seconds;
    canResend.value = false;

    stopCountdown(); // Clear any existing interval
    countdownInterval = window.setInterval(() => {
      if (countdown.value > 0) {
        countdown.value--;
      } else {
        canResend.value = true;
        stopCountdown();
      }
    }, 1000);
  }

  function stopCountdown() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = undefined;
    }
  }

  function resetCountdown() {
    countdown.value = initialSeconds;
    canResend.value = false;
    stopCountdown();
  }

  function formatCountdown() {
    const minutes = Math.floor(countdown.value / 60);
    const remainingSeconds = countdown.value % 60;
    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  }

  return {
    countdown,
    canResend,
    startCountdown,
    stopCountdown,
    resetCountdown,
    formatCountdown,
  };
}

export const focusNext = (index: number) => {
  const inputs = document.querySelectorAll(
    ".otp-box"
  ) as NodeListOf<HTMLInputElement>;
  const currentInput = inputs[index];

  if (currentInput.value.length === 1 && index < inputs.length - 1) {
    const nextInput = inputs[index + 1];
    nextInput.focus();
  }
};
