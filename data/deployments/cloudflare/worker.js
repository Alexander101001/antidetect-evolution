
addEventListener('scheduled', event => {
  event.waitUntil(handleScheduled(event));
});

async function handleScheduled(event) {
  // Trigger evolution cycle via webhook
  await fetch('https://evolution.example.com/cycle');
}
