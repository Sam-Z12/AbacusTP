import React, { useEffect, useState } from "react";
import { fetchHome } from "../abacus_client/abacus_endpoints";
import '../styles/home.css'



export class MyHome extends React.Component {
    constructor(props){
        super(props);
        this.state = {title: '',
                    description: ''};
    
    }
    fetchHomeMessage = async () => {
        try{
            
            const home_message = await fetchHome();
            //const home_message_str = JSON.stringify(home_message)
            this.setState({title: home_message.title,
                        description: home_message.description})

        } catch (error){
            console.log(error)
        }
    }
    componentDidMount() {
        this.fetchHomeMessage()
    }
    render(){

        return(
            <div className="container">
                <div className="card">
                    <h1>
                        {this.state.title}
                    </h1>
                    <p>
                        {this.state.description}
                    </p>
                </div>
                <div className="card">
                    <h1>
                        Card Title
                    </h1>
                    <p>
                        Card Description
                    </p>
                </div>
            </div>
        )
    }
}