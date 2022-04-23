import React, { useEffect, useState } from "react";
import { fetchHome } from "./abacus_endpoints";





export class MyHome extends React.Component {
    constructor(props){
        super(props);
        this.state = {message: ''};
    
    }
    fetchHomeMessage = async () => {
        try{
            
            const home_message = await fetchHome();
            //const home_message_str = JSON.stringify(home_message)
            this.setState({message: home_message.message})
            console.log("Fetching Home Message")

        } catch (error){
            console.log(error)
        }
    }
    componentDidMount() {
        this.fetchHomeMessage()
    }
    render(){

        return(
            <div>
                {this.state.message}
            </div>
        )
    }
}