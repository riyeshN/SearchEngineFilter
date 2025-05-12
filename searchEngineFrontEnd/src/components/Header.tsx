import { Button, ButtonGroup } from "@mui/material";
import React, {useState} from "react"
import { useNavigate } from "react-router-dom";
import api from "../api/api";

const Header = () => {

    const [active, setActive] = useState('getUrls');
    const navigate = useNavigate();
    const [response, setResponse] = useState([]);
    const [loading, setLoading] = useState(false) 
    
    const onClickUpdateScrape = async () => {
        try {
            setLoading(true)
            const response = await api.get('searchFilter/get_html_data')
            const flatUrls = response.data.urls.flat()
            console.log("our response", response, flatUrls);
            setResponse(flatUrls);
            setLoading(false)
        }catch(error) {
            console.log(error);
            setLoading(false)
        }
    }

    const onClickGetUrls = () => {
        setActive('getUrls');
        navigate('/');
    }

    const onClickScrapeUrls = () => {
        setActive('scrapeUrls');
        navigate('/ScrapeUrls');
    }

    

    return (
        <div style={{display: 'flex', justifyContent: 'flex-end'}}>
            <ButtonGroup variant="outlined" >
                <Button onClick={onClickGetUrls} color ={active === 'getUrls' ? 'error' : 'primary'}>Get URLS</Button>
                <Button onClick={onClickScrapeUrls} color ={active === 'scrapeUrls' ? 'error' : 'primary'}>Scrape URLS</Button>
                <Button onClick={onClickUpdateScrape} disabled={loading} color='secondary'>{loading ? 'Loading' : 'UPDATE KEYWORD DATA'}</Button>
            </ButtonGroup>
        </div>
    );
}

export default Header