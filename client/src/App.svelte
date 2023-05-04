<script>
	import { onMount } from "svelte";
	import Ad from "./Ad.svelte";

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
		ads = await response.json();

		ads.sort((a, b) => new Date(b.posted_on) - new Date(a.posted_on));

		console.log(displayedAds[0]);
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

	{#each displayedAds as ad}
		<Ad {ad} />
	{/each}
</main>

<style>
	.filters {
		margin: 1rem auto;
	}

	main {
		max-width: 580px;
		margin: 0 auto;
	}
</style>
