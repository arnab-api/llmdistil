<script>
    import AttnVis from './AttnVis.svelte';
    import {onMount} from 'svelte';
	export let prompt = "A quick brown fox jumps over the lazy dog";
    export let attnMatrix = null;

    export async function getAttnMatrix() {
        try {
            const response = await fetch(
                "http://localhost:5050/attnmatrix?prompt=" + encodeURIComponent("<|endoftext|> " + prompt)
            );
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            const data = await response.json();
            attnMatrix = data;
            console.log('Attention matrix:', attnMatrix);

        } catch (error) {
            console.error('Failed to fetch attention matrix:', error);
            attnMatrix = null;
        }
    }
    onMount(() => {
		getAttnMatrix(prompt);
	});

    function handleInput(event) {
        // Automatically resize textarea to fit content
        event.target.style.height = 'auto';
        event.target.style.height = `${event.target.scrollHeight}px`;
    }
</script>

<div class="outer-container">
    <div class="input-section">
        <textarea class="prompt-input" bind:value={prompt} on:input={handleInput} placeholder="Enter prompt"></textarea>
    </div>
    <div class="button-container">
        <button class="action-button" on:click={getAttnMatrix}>Go</button>
    </div>
    <AttnVis {attnMatrix} />
</div>

<style>
    .outer-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        width: 100%; /* Ensures the container takes the full width of the viewport */
    }

    .input-section {
        width: 100%; /* Full width of the container */
        padding: 0 10px; /* Slight padding on the sides */
    }

    .prompt-input {
        width: 100%; /* Makes textarea take up all of the container's width */
        min-height: 100px; /* Minimum height */
        resize: none; /* Prevent manual resize */
        padding: 10px; /* Comfortable padding inside the textarea */
        box-sizing: border-box; /* Includes padding in the width */
    }

    .button-container {
        display: flex;
        justify-content: center; /* Centers the button horizontally */
        width: 100%; /* Full width of the container */
    }

    .action-button {
        padding: 10px 20px;
        cursor: pointer; /* Makes it clear it's clickable */
        margin-top: 10px; /* Space above the button */
    }
</style>