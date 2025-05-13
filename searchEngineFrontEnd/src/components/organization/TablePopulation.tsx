import { FormControl, InputLabel, MenuItem, Select, SelectChangeEvent, Stack, Box, TableContainer, Table, Paper, TableHead, TableRow, TableCell, TableBody, Typography } from '@mui/material';
import React, { useState } from 'react'

const TablePopulation = ({urlList}: {urlList: any[]}) => {
    const groupBySearchEngine = new Map<string, any[]>()

    urlList.forEach((item) => {
        if(!groupBySearchEngine.has(item.searchEngine)){
            groupBySearchEngine.set(item.searchEngine, [])
        }
        groupBySearchEngine.get(item.searchEngine)!.push(item)
    })
    console.log("we got", groupBySearchEngine);

    const searchEngines = Array.from(groupBySearchEngine.keys())
    const [selectedEngine, setSelectedEngine] = useState(searchEngines[0] || '')
    const handleChange = (event: SelectChangeEvent) => {
        setSelectedEngine(event.target.value)
      }

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
        {groupBySearchEngine.has(selectedEngine) ? (
          <TableContainer component={Paper} sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead sx={{ backgroundColor: 'primary.main' }}>
                <TableRow>
                  {Object.keys(groupBySearchEngine.get(selectedEngine)![0]).map(
                    (key) => (
                      <TableCell key={key} sx={{ color: 'white', fontWeight: 'bold' }}>{key}</TableCell>
                    )
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {groupBySearchEngine.get(selectedEngine)!.map((item, idx) => (
                  <TableRow key={idx}>
                    {Object.values(item).map((val, i) => (
                      <TableCell key={i}>{String(val)}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography>No data available for selected engine.</Typography>
        )}
      </Box>
    </Stack>
    );
}

export default TablePopulation;