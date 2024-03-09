<script>
    let rand = -1;
    function getRand() {
        fetch("http://localhost:5000/rand")
            .then((d) => d.text())
            .then((d) => (rand = d));
        console.log("rand: ", rand);
    }
</script>

<h1>Your number is {rand}!</h1>
<button on:click={getRand}>Get a random number</button>
