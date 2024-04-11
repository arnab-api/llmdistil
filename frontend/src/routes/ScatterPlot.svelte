<script>
	import * as d3 from 'd3'
	import Axis from './Axis.svelte';

	// data comes from the load function in +page.js
	export let dataset;

	// default features to visualize
	export let xFeature;
	export let yFeature;
	export let colorFeature;
	export let color;
	export let highlightedPlayer;

	const margin = {top: 35, right: 20, bottom: 50, left: 60};
	let borderBoxSize;

	$: width = borderBoxSize ? Math.min(borderBoxSize[0].blockSize, borderBoxSize[0].inlineSize) : 400
	$: height = borderBoxSize ? Math.min(borderBoxSize[0].blockSize, borderBoxSize[0].inlineSize) : 400


	$: x = d3
		.scaleLinear()
		.domain(d3.extent(dataset, (d) => d[xFeature]))
		.range([margin.left, width - margin.right]);
	
	$: y = d3
		.scaleLinear()
		.domain(d3.extent(dataset, (d) => d[yFeature]))
		.range([height - margin.bottom, margin.top]);
</script>

<div class="scatterplot" bind:borderBoxSize>
	<svg {width} {height}>
		<g>
			{#each dataset as d}
				<circle
					cx = {x(d[xFeature])}
					cy = {y(d[yFeature])}
					fill = {color(d[colorFeature])}
					r = {3}
				/>
			{/each}

			{#if highlightedPlayer}	
				<circle
					cx = {x(highlightedPlayer[xFeature])}
					cy = {y(highlightedPlayer[yFeature])}
					fill = {color(highlightedPlayer[colorFeature])}
					r = {6}
					stroke={'black'}
					stroke-width={2}
				/>
			{/if}
		</g>

		<Axis scale={x} {width} {height} {margin} orientation="bottom" label={xFeature}/>
		<Axis scale={y} {width} {height} {margin} orientation="left" label={yFeature}/>
	</svg>
</div>

<style>
	.scatterplot {
		flex: 1;
		height: 100%;
	}
	circle {
		transition:
			cx 250ms,
			cy 250ms;
	}
</style>
