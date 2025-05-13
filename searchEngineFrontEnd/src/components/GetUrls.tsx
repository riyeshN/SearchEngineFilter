import React, { useState } from "react";
import { Button, Grid, TextField, Box, Stack } from "@mui/material";
import api from "../api/api";
import TablePopulation from "./organization/TablePopulation";

const GetUrls = () => {
	const [searchVal, setSearchVal] = useState("");
	const [loading, setLoading] = useState(false);
	const [listOfUrls, setListOfUrls] = useState([]);
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
		} catch (error) {
			console.log("ERROR", error);
		} finally {
			setLoading(false);
		}
	};

	const renderTable = () => {
		if (listOfUrls.length > 0) {
			return <TablePopulation urlList={listOfUrls} />;
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

				<Grid size={12}>
					<Box sx={{ width: "100%", marginTop: 3 }}>{renderTable()}</Box>
				</Grid>
			</Grid>
		</Box>
	);
};

export default GetUrls;
