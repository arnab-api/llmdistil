<script>
    import AttnVis from "./AttnVis.svelte";
    import { onMount } from "svelte";
    import bufferingGif from "../assets/buffering.gif";

    export let prompt = "A quick brown fox jumps over the lazy dog";
    export let attnMatrix = null;
    export let attn_vis_container;
    export let n_views = "3";

    export async function getAttnMatrix() {
        try {
            attnMatrix = null;
            console.log("Fetching attention matrix for prompt:", prompt);
            attn_vis_container.innerHTML = `<img class="buffering-gif" src="${bufferingGif}" alt="Buffering..." />`;
            const response = await fetch(
                "http://10.200.205.169:5050/attnmatrix?prompt=" +
                    encodeURIComponent("<|endoftext|> " + prompt)
            );
            if (!response.ok) {
                throw new Error(
                    "Network response was not ok: " + response.statusText
                );
            }
            const data = await response.json();
            attnMatrix = data;
            console.log("Attention matrix:", attnMatrix);
        } catch (error) {
            console.error("Failed to fetch attention matrix:", error);
            attnMatrix = null;
        }
    }
    onMount(() => {
        getAttnMatrix(prompt);
    });

    function handleInput(event) {
        // Automatically resize textarea to fit content
        event.target.style.height = "auto";
        event.target.style.height = `${event.target.scrollHeight}px`;
    }
</script>

<div class="prompt-and-control">
    <textarea
        class="prompt-input"
        bind:value={prompt}
        on:input={handleInput}
        placeholder="Enter prompt"
    ></textarea>
    <div class="controls">
        <div class="button-container">
            &nbsp;&nbsp;
            <button class="action-button" on:click={getAttnMatrix}>Go</button>
        </div>
        <div class="nview-control">
            <label for="nview-select">#Heads</label> &nbsp;
            <select id="nview-select" bind:value={n_views}>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3" selected>3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
            </select>
        </div>
    </div>

    <div class="attn-vis-container">
        <AttnVis {attnMatrix} bind:attn_vis_container bind:n_views />
    </div>
</div>

<style>
    .prompt-and-control {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        width: 100%; /* Adjust if needed to match the design */
    }

    .prompt-input {
        width: 100%; /* Ensures textarea takes up all of the container's width */
        min-height: 100px; /* Minimum height */
        resize: none; /* Disallow manual resizing */
        padding: 10px; /* Padding inside the textarea */
        box-sizing: border-box; /* Includes padding in the width */
        margin-bottom: 5px; /* Ensure there is space below textarea */
    }

    .button-container {
        display: flex;
        justify-content: center; /* Centers the button horizontally */
        width: 100%; /* Ensures full width */
        margin-top: 10px; /* Adds space above the button */
    }

    .action-button {
        padding: 10px 20px;
        cursor: pointer; /* Indicates it's clickable */
    }

    .controls {
        display: flex;
        justify-content: space-between; /* Keeps space between elements */
        align-items: center;
        width: 100%; /* Ensures full-width container */
    }

    #nview-select {
        /* padding: 10px; /* Padding inside the dropdown */
        /* display: block; /* Ensures that the select takes up only necessary space */
        /* margin-left: auto; /* Pushes the dropdown to the right */
    }

    .nview-control {
        display: flex;
        /* align-items: center; */
    }
</style>
