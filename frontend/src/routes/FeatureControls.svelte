<script>
	import FeatureSelect from "./FeatureSelect.svelte";

	export let dataset;
	export let xFeature;
	export let yFeature;
	export let colorFeature;

	$: axisColumns = dataset.columns.filter((col) => typeof dataset[0][col] === 'number')
	$: colorColumns = dataset.columns.filter((col) => {
		const numUnique = new Set(dataset.map((d) => d[col])).size;
		return numUnique <= 10;
	});


</script>
<!-- can be dangerous use to use bind to pass values from child to parent. as the data flows both ways -->
<div class="container">
	<FeatureSelect bind:value={xFeature} options={axisColumns} label={"X-axis"}></FeatureSelect> 
	<FeatureSelect bind:value={yFeature} options={axisColumns} label={"Y-axis"}></FeatureSelect>
	<FeatureSelect bind:value={colorFeature} options={colorColumns} label={"Color"}></FeatureSelect>
</div>

<style>
	div {
		display: flex;
		align-items: center;
		gap: 1em;
	}
</style>