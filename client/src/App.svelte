<script>
	import { onMount } from "svelte";
	import Ad from "./Ad.svelte";

	let api_error = "";
	let api_error_text = "";

	// TODO: filter for bad words in frontend instead of backend
	let desiredDistricts = [
		"Kreuzberg",
		"Neukölln",
		"Mitte",
		"Wedding",
		"Tempelhof",
		"Schöneberg",
	];
	let age = 24;

	let filterByAge = true;
	let filterDistricts = true;
	let filterByPermanent = true;

	let ads = [];
	$: displayedAds = ads.filter(
		(ad) =>
			(ad.available_for === "dauerhaft" || !filterByPermanent) &&
			(desiredDistricts.includes(ad.district) || !filterDistricts) &&
			((age >= ad.min_age && age <= ad.max_age) || !filterByAge)
	);

	onMount(async () => {
		const response = await fetch("./api/v0/ads");

		if (!response.ok) {
			api_error = response.status;
			api_error_text = ;
			return;
		}

		ads = await response.json();
	});
</script>

<main>
	<h1>Hello Martin!</h1>

	<div class="filters">
		<label>
			<input type="checkbox" bind:checked={filterByPermanent} />
			Show only permanent offers
		</label>
		<label>
			<input type="checkbox" bind:checked={filterDistricts} />
			Show only good locations
		</label>
		<label>
			<input type="checkbox" bind:checked={filterByAge} />
			Filter by age
		</label>
	</div>

	{#if api_error}
		<div class="api-error">
			<div class="api-error-title">{api_error}</div>
			<div class="api-error-desc">{api_error_text}</div>
		</div>
	{/if}

	{#each displayedAds as ad}
		<Ad {ad} />
	{/each}
</main>

<style>
	.api-error {
		background-color: #ffcdd2;
		border: 1px solid #e53935;
		border-radius: 5px;
		padding: 0.5rem 0.75rem;
	}
	.api-error-title {
		font-weight: bold;
	}
	.filters {
		margin: 1rem auto;
	}

	main {
		max-width: 680px;
		margin: 0 auto;
	}
</style>
