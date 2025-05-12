import React from 'react'
import { Button, Grid, TextField, Box } from '@mui/material'

const GetUrls = () => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', padding: 5 }}>
      <Grid container spacing={1} alignItems="center" maxWidth="md">
        <Grid size={6}>
          <TextField
            id="searchGetUrls"
            label="Search"
            variant="outlined"
            fullWidth
            sx={{ borderRadius: '50px', backgroundColor: 'white' }}
          />
        </Grid>
        
        <Grid size={2}>
          <Button
            variant="contained"
            fullWidth
            sx={{
              height: '100%',
              textTransform: 'none',
              fontWeight: 'bold',
              borderRadius: '50px'
            }}
          >
            Search
          </Button>
        </Grid>
      </Grid>
    </Box>
  )
}

export default GetUrls