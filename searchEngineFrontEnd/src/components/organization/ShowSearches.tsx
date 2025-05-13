import {
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	SelectChangeEvent,
	Stack,
	Box,
	Typography,
	Card,
	CardContent,
	CardActions,
	CardActionArea,
	Pagination,
} from "@mui/material";
import React, { useState } from "react";

const ShowSearches = ({ urlList }: { urlList: any[] }) => {
	const [page, setPage] = useState(1);
	const itemsPerPage = 10;

	const handlePageChange = (
		_event: React.ChangeEvent<unknown>,
		value: number
	) => {
		setPage(value);
	};

	const groupBySearchEngine: Map<string, any[]> = new Map();

	urlList.forEach((item) => {
		if (!groupBySearchEngine.has(item.searchEngine)) {
			groupBySearchEngine.set(item.searchEngine, []);
		}
		groupBySearchEngine.get(item.searchEngine)!.push(item);
	});

	const searchEngines = Array.from(groupBySearchEngine.keys());
	const [selectedEngine, setSelectedEngine] = useState(searchEngines[0] || "");

	const handleChange = (event: SelectChangeEvent) => {
		setSelectedEngine(event.target.value);
		setPage(1); // reset page when changing engine
	};

	const handleCardClick = (url: string) => {
		window.open(url, "_blank", "noopener,noreferrer");
	};

	const filteredItems = (() => {
		const seen = new Set<string>();
		return (groupBySearchEngine.get(selectedEngine) ?? [])
			.filter((item) => item.ad_promo === false)
			.filter((item) => {
				if (seen.has(item.url)) return false;
				seen.add(item.url);
				return true;
			});
	})();

	const paginatedItems = filteredItems.slice(
		(page - 1) * itemsPerPage,
		page * itemsPerPage
	);

	const searchEngineWithThisLink = (url: string): string => {
		const engines: string[] = [];

		for (const [engine, items] of groupBySearchEngine.entries()) {
			if (items.some((item) => item.url === url)) {
				engines.push(engine);
			}
		}

		return engines.join(", ");
	};

	return (
		<Stack sx={{ width: "100%" }} spacing={2}>
			<Box sx={{ width: "100%" }}>
				<FormControl fullWidth>
					<InputLabel id="engine-label">Search Engine</InputLabel>
					<Select
						labelId="engine-label"
						id="engine-select"
						value={selectedEngine}
						label="Search Engine"
						onChange={handleChange}
					>
						{searchEngines.map((engine) => (
							<MenuItem key={engine} value={engine}>
								{engine}
							</MenuItem>
						))}
					</Select>
				</FormControl>
			</Box>

			<Box sx={{ width: "100%", margin: "0 auto" }}>
				{filteredItems.length > 0 ? (
					<>
						{paginatedItems.map((item, idx) => (
							<Card key={idx} sx={{ mb: 2 }}>
								<CardActionArea onClick={() => handleCardClick(item.url)}>
									<CardContent>
										<Typography
											gutterBottom
											variant="h5"
											component="div"
											color="primary"
										>
											{item.title}
										</Typography>
										<Typography variant="body2" color="text.secondary">
											{item.desc}
										</Typography>
									</CardContent>
									<CardActions>
										<Typography variant="caption" color="text.secondary">
											COUNT: {item.count_of_appearance} — TIME SEARCHED:{" "}
											{item.time_searched} -- ENGINE WITH THIS LINK{" "}
											{searchEngineWithThisLink(item.url)}
										</Typography>
									</CardActions>
								</CardActionArea>
							</Card>
						))}
						<Pagination
							count={Math.ceil(filteredItems.length / itemsPerPage)}
							page={page}
							onChange={handlePageChange}
							color="primary"
							sx={{ mt: 2 }}
						/>
					</>
				) : (
					<Typography>No data available for selected engine.</Typography>
				)}
			</Box>
		</Stack>
	);
};

export default ShowSearches;
