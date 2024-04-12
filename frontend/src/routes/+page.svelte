<script>
	import './style.css';
	import InputPrompt from './InputPrompt.svelte';

	export let prompt = "A quick brown fox jumps over the lazy dog";
    export let attnMatrix = null;
	export let attn_vis_container;
</script>

<div class="main"> 
	<div class="container">
		<InputPrompt 
			bind:prompt 
			bind:attnMatrix
			bind:attn_vis_container
		/>
	</div>
</div>

<style>
	.container {
		/* set the font */
		font-family: system-ui, sans-serif;
		font-size: 16px;

		height: 100vh;
		width: 100vw;

		display: flex;
		flex-direction: column;
		gap: 2em;
		
		padding: 2em;
	}

	.main {
		flex: 1; /* use the rest of vertical space not used by header */
		min-height: 0;  /*allowing main to shrink*/
		/* place children next to each other */
		display: flex;
		gap: 2em;
		/* background-color: #fffeda; */
	}

	.header {
		display: flex;
		align-items: center;
		gap: 2em;
	}
</style>