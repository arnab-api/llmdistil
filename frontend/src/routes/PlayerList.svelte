<script>
	import './style.css';

	// data comes from the load function in +page.js
	export let dataset;
	export let onhover;
</script>

<ul>
	{#each dataset as player}
		<li 
			on:mouseover={() => onhover(player)} 
			on:mouseleave={() => onhover(null)}
			on:focus={() => onhover(player)}
			on:focusout={() => onhover(null)}
		>
			{player.name} ({player.team})
		</li>
	{/each}
</ul>	

<style>
	ul {
		width: 18em;
		max-height: 100%; /*make list no taller than parent*/
		overflow: auto; /*should enable scrolling*/
		list-style: none;
		padding: 0;
	}
	li + li {
		margin-top: 0.5em;
	}

	li:hover {
		background-color: #dddddd;
		font-weight: bold;
	}
</style>
