async function sendMessage() {
    const promptInput = document.getElementById('prompt-input');
    const responseArea = document.getElementById('response-area');

    const prompt = promptInput.value;
    if (!prompt) {
        alert('プロンプトを入力してください。');
        return;
    }

    responseArea.innerText = '生成中...';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        responseArea.innerText = data.response;

    } catch (error) {
        console.error('Error:', error);
        responseArea.innerText = 'エラーが発生しました。';
    }
}