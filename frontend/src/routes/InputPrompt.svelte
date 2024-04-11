<script>
    import {onMount} from 'svelte';
	export let prompt = "A quick brown fox jumps over the lazy dog";
    export let attnMatrix = null;

    export async function getAttnMatrix() {
        try {
            const response = await fetch("http://localhost:5050/attnmatrix?prompt=" + encodeURIComponent(prompt));
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            const data = await response.json();
            attnMatrix = data;
            console.log('Attention matrix:', attnMatrix);
        } catch (error) {
            console.error('Failed to fetch attention matrix:', error);
            // Optionally, handle the error visually in UI
            attnMatrix = null;
        }
    }
    onMount(() => {
		getAttnMatrix(prompt);
	});

</script>

<div class="input-prompt">
    <input type="text" bind:value={prompt} id="prompt" name="prompt" placeholder={prompt}>
    <button on:click={getAttnMatrix}>Go</button>
</div>

<style>
    .input-prompt {
        display: flex;
        flex-direction: row;
        gap: 1em;
    }
</style>