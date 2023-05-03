<script>
	import { onMount } from "svelte";

	let ads = [];
	onMount(async () => {
		const response = await fetch("./api/v0/ads");
		ads = await response.json();

		ads.sort((a, b) => new Date(b.posted_on) - new Date(a.posted_on));

		console.log(ads);
	});
</script>

<main>
	<h1>Hello Martin!</h1>
	ads: Titel Kreuzberg | ab 1. Mai | unbefristet (farbe je nachdem ob gut oder
	schlecht)

	<ul>
		{#each ads as ad}
			<li>
				{ad.posted_on} <a href={ad.url}>{ad.title}</a>
				{ad.available_for}
			</li>
		{/each}
	</ul>
</main>

<style>
</style>
