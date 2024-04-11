<script>
    import * as d3 from 'd3';
    import {onMount} from 'svelte';

    export let attnMatrix = null;
    export let n_views = 3;
    export let remove_prefix_pad = false;
    export let selected_heads = null;


    let container;

    $: console.log("attnMatrix", attnMatrix);

    onMount(() => {
        if (!attnMatrix || attnMatrix.attention_matrices.length === 0) {
            console.error('Attention data is required');
            return;
        }
        const visualizationElement = visualize_multiple_attention(
            attnMatrix,
            remove_prefix_pad,
            n_views,
            selected_heads
        );
        container.appendChild(visualizationElement);
    });


    function visualize_multiple_attention(
        attention_mappings,
        remove_prefix_pad = false,
        n_views = 3, 
        selected_heads = null
    ) {
        console.log("selected heads", selected_heads)
        
        const colors = [
            d3.interpolateReds, d3.interpolateBlues, d3.interpolateGreens, 
            d3.interpolatePurples, d3.interpolateGreys, d3.interpolateOranges
        ]

        if(n_views > colors.length){
            throw `n_views more than ${colors.length} is not supported`
        }
        
        let num_layers = attention_mappings.attention_matrices.length
        let num_heads = attention_mappings.attention_matrices[0].length
        let tokens = attention_mappings.tokenized_prompt
        let TARGET_TOKEN = tokens.length - 1;

        if (remove_prefix_pad === true) {
            if (tokens[0] === "<|endoftext|>") {
            tokens = tokens.slice(1, )
            } 
            else{
            remove_prefix_pad = false
            }
        }

        // Function to draw tokens based on layer and head
        function drawTokens(
            target_idx, 
            layer_idx, head_idx, 
            container_div, color
        ) {
            const attention_matrix = attention_mappings.attention_matrices[layer_idx][head_idx];
            
            let attention_distribution = attention_matrix[target_idx]
            if (remove_prefix_pad === true) {
                attention_distribution = attention_distribution.slice(1,)
            }
        
            // Clear previous content
            container_div.html("");
            let color_scale = d3.scaleSequential()
                .domain([d3.min(attention_distribution), d3.max(attention_distribution)])
                .interpolator(color);
        
            tokens.forEach((src_token, i) => {
                let color_rgb = i <= target_idx ? color_scale(attention_distribution[i]) : "rgb(255, 255, 255)";
                let text_color = i <= target_idx ? "black" : "gray";
                    
                let style = `background: ${color_rgb}; color: ${text_color}; padding:2px;`; // Added padding for visibility
                if (i === target_idx) {
                    style += " border:1px solid black;";
                }
                    
                let token_div = container_div.append('div')
                    .attr("style", style)
                    .text(src_token);
            
                token_div.on('mouseenter', function() {
                    if (i !== target_idx) {
                        d3.select(this).style("border", "1px solid gray");
                    }
                });
            
                token_div.on('mouseleave', function() {
                    if (i !== target_idx) {
                        d3.select(this).style("border", "");
                    }
                });
            
                // Update target_idx and redraw tokens on click
                token_div.on('click', () => {
                    // drawTokens(i, layer_idx, head_idx, container_div, color); // Re-draw tokens with new target_idx
                    update_all_views(i)
                });
            });
        }

          // Outer container
        const main_container_div = d3.create('div')
            .attr("style", "display: flex; flex-wrap: wrap; flex-direction: column; gap: 1em; padding: 1em;");

        for(let view_no = 0; view_no < n_views; view_no++){ 
            const view_container_div = main_container_div.append('div').attr('id', `view_${view_no}`);
            const color = colors[view_no]
            let default_head = 0
            let default_layer = 0
            if (selected_heads !== null){
                console.log(">>>>", selected_heads)
                default_head = selected_heads[view_no][1]
                default_layer = selected_heads[view_no][0]
            }
    
            // Configuration container for selects
            const config_div = view_container_div.append('div')
                .attr("style", "display: flex; flex-wrap: wrap; gap: 0.5em; padding: 0.5em;");

            // Layer Select
            const layer_config_div = config_div.append('div').attr("style", "display: flex;")
            layer_config_div.append('label')
                .attr('for', 'layer-select')
                .text('Layer: ');
            
            const layer_select = layer_config_div.append('select').attr('id', 'layer-select');
            for (let i = 0; i < num_layers; i++){
                if(i == default_layer) layer_select.append('option').text(i).attr('value', i).attr("selected", "selected");
                else layer_select.append('option').text(i).attr('value', i);
            }    
    
            // Head Select
            const head_config_div = config_div.append('div').attr("style", "display: flex;")
            head_config_div.append('label')
                .attr('for', 'head-select')
                .text('Head: ');
        
            const head_select = head_config_div.append('select').attr('id', 'head-select');
            for (let i = 0; i < num_heads; i++){
                if(i == default_head) head_select.append('option').text(i).attr('value', i).attr("selected", "selected");
                else head_select.append('option').text(i).attr('value', i);
            }    

            // Visualization container
            const token_container = view_container_div.append('div')
                .attr("style", "display: flex; flex-wrap: wrap;")
                .attr("id", "tokens");
    
            // React to selections
            function updateVisualization() {
                const selected_layer = +layer_select.node().value;
                const selected_head = +head_select.node().value;
                
                let target_idx = TARGET_TOKEN;
            
                drawTokens(target_idx, selected_layer, selected_head, token_container, color);
            }
    
            // Listen for changes and update
            layer_select.on('change', updateVisualization);
            head_select.on('change', updateVisualization);
    
            // Initial drawing
            updateVisualization();
        }

        function update_all_views(target_idx){
            TARGET_TOKEN = target_idx
            for(let view_no = 0; view_no < n_views; view_no++){
                const layer_selector = d3.select(`#view_${view_no}`).select("#layer-select")
                const head_selector = d3.select(`#view_${view_no}`).select("#head-select")
                const token_view = d3.select(`#view_${view_no}`).select("#tokens")
                
                console.log(view_no, `L: ${layer_selector.node().value}`, `H: ${head_selector.node().value}`)

                drawTokens(
                    target_idx, 
                    layer_selector.node().value, head_selector.node().value,
                    token_view, colors[view_no]
                )
            }
        }
        console.log("main_container_div")
        return main_container_div.node();
    }
</script>

<div bind:this={container}>
{#if attnMatrix}
    <div id="main-container"></div>
{:else}
    <p>Loading...</p>
{/if
}
</div>