<script>
	import * as d3 from 'd3'
	import Axis from './Axis.svelte';

	// data comes from the load function in +page.js
	export let dataset;

	// default features to visualize
	export let feature;
	export let color;

	const margin = {top: 25, right: 20, bottom: 50, left: 60};
	let borderBoxSize;

	$: width = borderBoxSize ? Math.min(borderBoxSize[0].blockSize, borderBoxSize[0].inlineSize) : 400
	$: height = borderBoxSize ? Math.min(borderBoxSize[0].blockSize, borderBoxSize[0].inlineSize) : 400


	$: counts = d3.rollup(
		dataset,
		(g) => g.length,
		(d) => d[feature]
	);

	$: maxCount = d3.max(counts.values())

	$: x = d3
		.scaleLinear()
		.domain([0, maxCount])
		.range([margin.left, width - margin.right]);
	
	$: y = d3
		.scaleBand()
		.domain(color.domain())
		.range([margin.top, height - margin.bottom])
		.padding(0.1);
</script>

<div class="barchart" bind:borderBoxSize>
	<svg {width} {height}>
		<g>
			{#each counts as [category, count]}
				<rect
					x = {x(0)}
					y = {y(category)}
					height = {y.bandwidth()}
					width = {x(count) - x(0)}
					fill = {color(category)}
				/>
			{/each}
		</g>

		<Axis scale={x} {width} {height} {margin} orientation="bottom" label={'Count'}/>
		<Axis scale={y} {width} {height} {margin} orientation="left"/>
	</svg>
</div>

<style>
	.barchart {
		flex: 1;
		height: 100%;
	}
</style>