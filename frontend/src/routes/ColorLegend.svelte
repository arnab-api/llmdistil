<script>
	export let color;
</script>

<div class="swatches">
	{#each color.domain() as d}
		<div class="swatch">
			<div class="square" style:background-color={color(d)}></div>
			<div>{d}</div>
		</div>
	{/each}
</div>

<style>
	.swatch{
		display: flex;
		align-items: center;
		gap: 0.25em;
	}

	.swatches{
		display: flex;
		align-items: center;
		gap: 1em;
	}

	.square{
		width: 15px;
		height: 15px;
	}
</style>