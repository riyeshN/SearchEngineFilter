import React, { useState } from "react";
import { Button, Grid, TextField, Box, Stack, Typography } from "@mui/material";
import api from "../api/api";
import ShowSearches from "./organization/ShowSearches";

const GetUrls = () => {
	const [searchVal, setSearchVal] = useState("");
	const [loading, setLoading] = useState(false);
	const [listOfUrls, setListOfUrls] = useState([]);
	const [listOfStats, setListOfStats] = useState({});
	const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setSearchVal(e.target.value);
	};

	const handleOnClick = async () => {
		try {
			setLoading(true);
			console.log("sending request for:", searchVal);
			const response = await api.get(
				"searchFilter/get_list_of_links_for_keyword",
				{
					params: {
						keyword: searchVal,
					},
				}
			);
			setListOfUrls(response.data.data);
			console.log("urls", response.data.data);

			const response2 = await api.get("searchFilter/get_list_of_ads_none_ads", {
				params: {
					keyword: searchVal,
				},
			});

			const searchEngineStats = {};
			response2.data.data.forEach((element) => {
				const engine = element.searchEngineName_id;
				const adPromo = element.ad_promo;
				const count = element["COUNT(*)"];

				if (!searchEngineStats[engine]) {
					searchEngineStats[engine] = {};
				}
				searchEngineStats[engine][adPromo] = count;
			});
			setListOfStats(searchEngineStats);
			console.log("urls", searchEngineStats);
		} catch (error) {
			console.log("ERROR", error);
		} finally {
			setLoading(false);
		}
	};

	const renderTable = () => {
		if (listOfUrls.length > 0) {
			return <ShowSearches urlList={listOfUrls} />;
		} else return null;
	};

	return (
		<Box
			sx={{
				display: "flex",
				justifyContent: "center",
				padding: 5,
				width: "95%",
			}}
		>
			<Grid container spacing={1} alignItems="center" sx={{ width: "90%" }}>
				<Grid size={10}>
					<TextField
						id="searchGetUrls"
						label="Search"
						value={searchVal}
						onChange={handleSearchChange}
						variant="outlined"
						fullWidth
						sx={{ borderRadius: "50px", backgroundColor: "white" }}
					/>
				</Grid>

				<Grid size={2}>
					<Button
						variant="contained"
						fullWidth
						disabled={loading}
						sx={{
							height: "100%",
							textTransform: "none",
							fontWeight: "bold",
							borderRadius: "50px",
						}}
						onClick={handleOnClick}
					>
						{loading ? "Loading" : "Search"}
					</Button>
				</Grid>
				<Grid container spacing={2}>
					{Object.entries(
						listOfStats as Record<string, Record<string, number>>
					).map(([engine, stats]) => (
						<Grid size={6} key={engine}>
							<Typography>
								{`${engine} - Ads: ${stats["true"] ?? 0} - Not Ads: ${
									stats["false"] ?? 0
								} - Percent Ads ${(
									(stats["true"] ?? 0) / (stats["false"] ?? 0)
								).toFixed(2)}`}
							</Typography>
						</Grid>
					))}
				</Grid>
				<Grid size={12}>
					<Box sx={{ width: "100%", marginTop: 3 }}>{renderTable()}</Box>
				</Grid>
			</Grid>
		</Box>
	);
};

export default GetUrls;
