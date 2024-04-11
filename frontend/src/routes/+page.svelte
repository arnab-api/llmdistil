<script>
	import './style.css';
	import PlayerList from './PlayerList.svelte';
	import ScatterPlot from './ScatterPlot.svelte';
	import BarChart from './BarChart.svelte';
	import * as d3 from 'd3'
	import ColorLegend from './ColorLegend.svelte';
	import FeatureControls from './FeatureControls.svelte';

	import InputPrompt from './InputPrompt.svelte';
	import AttnVis from './AttnVis.svelte';

	// data comes from the load function in +page.js
	export let data;

	export let prompt = "some other prompt lorem ipsum";
    export let attnMatrix = null;

	// default features to visualize
	let xFeature = 'strikeout';
	let yFeature = 'hit';
	let colorFeature = 'all_star';

	let highlightedPlayer = null;

	function onhover(player) {
		highlightedPlayer = player;
	}

	$: catagories = d3.groupSort(
		data.dataset,
		(g) => g.length,
		(d) => d[colorFeature]
	).reverse()

	$: color = d3.scaleOrdinal().domain(catagories).range(d3.schemeTableau10)
</script>

<div class="container">
	<InputPrompt 
		bind:prompt 
		bind:attnMatrix
	/>
	<AttnVis 
		bind:attnMatrix
	/>

	<!-- <div class="header">
		<FeatureControls dataset={data.dataset} bind:xFeature bind:yFeature bind:colorFeature/>
		<ColorLegend {color}/>
	</div>
	<div class="main">
		<PlayerList dataset = {data.dataset} {onhover}/>
		<ScatterPlot dataset = {data.dataset} {xFeature} {yFeature} {colorFeature} {color} {highlightedPlayer}/>
		<BarChart dataset = {data.dataset} feature={colorFeature} {color} />
	</div> -->
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
	}

	.header {
		display: flex;
		align-items: center;
		gap: 2em;
	}
</style>