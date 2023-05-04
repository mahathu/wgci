<script>
    export let ad;

    function toggleDescription(e) {
        document.getElementById(`${ad.title}-desc`).classList.toggle("hidden");
    }
</script>

<div class="property-container">
    <div class="property-title">
        <!-- svelte-ignore a11y-missing-attribute -->
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <a on:click={toggleDescription}>{ad.title}</a>
    </div>
    <div id="{ad.title}-desc" class="property-description hidden">
        "{ad.description}"
    </div>
    <div class="property-details">
        <a href={ad.url}>[contact]</a>
        <span>{ad.district}</span>
        <span>vom {ad.posted_on}</span>
        <span>verfügbar ab: {ad.available_from}</span>
        <span>{ad.available_for}</span>
        <span>{ad.min_age} - {ad.max_age}</span>
    </div>
</div>

<style>
    .property-container {
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #ccc;
    }

    .property-title {
        font-size: 1.25rem;
        cursor: pointer;
    }

    .property-description {
        margin-top: 0.35rem;
        font-style: italic;
    }
    .hidden {
        display: none;
    }

    .property-details {
        margin-top: 0.5rem;
        font-size: 0;
    }

    .property-details > * {
        font-size: 1rem;
    }

    .property-details > * + *::before {
        content: "·";
        margin: 0 0.25rem;
    }
</style>
