import React from "react"
import {Nav, NavLink, NavMenu, NavBtnLink, NavBtn} from './navbar_styles'

export const Navbar = () => {
    return(
        <>
           <Nav>
               <NavLink to="/">

               </NavLink>
               <NavMenu>
                   <NavLink to="Home" activeStyle>
                       Home
                   </NavLink>
                   <NavLink to="other1" activeStyle>
                       Other
                   </NavLink>
                   <NavLink to="other2" activeStyle>
                       Other 
                   </NavLink>
               </NavMenu>
           </Nav>
        </>
    )
}