import React, { useEffect, useState } from 'react'
import { Button, Grid, TextField, Box, Stack } from '@mui/material'
import api from '../api/api';
import TablePopulation from './organization/TablePopulation';

const ScrapeUrls = () => {
    const [searchVal, setSearchVal] = useState('');
    const [urlSize, setUrlSize] = useState<number>(0);
    const [listOfUrls, setListOfUrls] = useState([]);
    const [loading, setLoading] = useState(false) 
    const handleSearchChange = ( e: React.ChangeEvent<HTMLInputElement> ) => {
        setSearchVal(e.target.value);
    }

    const handleSizeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = Math.abs(Number(e.target.value));
        const minValue = Math.min(value, 300);
        setUrlSize(minValue);
    }

    const handleOnClick = async () => {
        try {
            setLoading(true)
            const response = await api.get('searchFilter/', {
                params: {
                    'keyword': searchVal,
                    'url_size': urlSize
                },
            })
            const flatUrls = response.data.urls.flat()
            console.log(response.data. flatUrls);
            setListOfUrls(flatUrls);
            setLoading(false)
        }catch(error) {
            console.log(error);
            setLoading(false)
        }
    }

    const renderTable = () => {
        if(listOfUrls.length > 0){
            return <TablePopulation urlList={listOfUrls}/>
        }else return null
    }

    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', padding: 5 }}>
            <Stack spacing={2}>
                
                <Grid container spacing={1} alignItems="center" maxWidth="md">
                    <Grid size={6}>
                    <TextField
                        id="searchGetUrls"
                        label="Search"
                        value={searchVal}
                        variant="outlined"
                        onChange={handleSearchChange}
                        fullWidth
                        sx={{ borderRadius: '50px', backgroundColor: 'white' }}
                    />
                    </Grid>
                    <Grid size={4}>
                    <TextField
                        id="size"
                        label="URL Size"
                        variant="outlined"
                        onChange={handleSizeChange}
                        fullWidth
                        value={urlSize}
                        type="number"
                        inputProps={{min:1}}
                    />
                    </Grid>
                    <Grid size={2}>
                    <Button
                        disabled = {loading}
                        variant="contained"
                        fullWidth
                        sx={{
                        height: '100%',
                        textTransform: 'none',
                        fontWeight: 'bold',
                        borderRadius: '50px'
                        }}
                        onClick={handleOnClick}
                    >
                        {loading ? 'Loading' : 'Scrape'}
                    </Button>
                    </Grid>
                </Grid>

                <Grid>
                    <Box sx={{ width: '95%', margin: '0 auto' }}>
                        {renderTable()}
                    </Box>
                </Grid>
            </Stack>
        </Box>
    )
}

export default ScrapeUrls;