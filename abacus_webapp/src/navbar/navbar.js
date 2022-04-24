import React from "react"
import {Nav, NavLink, NavMenuL, NavMenuR } from './navbar_styles'

export const Navbar = () => {
    return(
        <>
           <Nav>
               <NavMenuL>
                    <NavLink to="/">
                        Home
                    </NavLink>
                    <NavLink to="/paper_trade" >
                        Paper Trading
                    </NavLink>
                    <NavLink to="/algorithms">
                        Algorithms
                    </NavLink>
                </NavMenuL>
                <NavMenuR>
                    <NavLink to="/login" >
                    Login
                    </NavLink>
                </NavMenuR>
               
           </Nav>
        </>
    )
}