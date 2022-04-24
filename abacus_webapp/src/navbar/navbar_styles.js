import styled from 'styled-components';
import { NavLink as Link} from 'react-router-dom';

export const Nav = styled.div`
background: linear-gradient(to left, #10021cd9, #0a0214d9);
height: 50px;
display: flex;
flex-direction: row;
justify-content: space-between;
padding: 0.5rem; calc((100vw - 1000px) / 2);
z-index: 10;
align-item: center;
border-style: none none solid none;
border-width: 1.5px;
border-color: rgba(255, 0, 157, .05);

`

export const NavLink = styled(Link)`
color: rgba(80, 51, 130, 1);
display: flex;
align-items: center;
text-decoration: none;
padding: 1rem;S
height: 100%;
cursor: pointer;
font-family: Verdana, Geneva, Tahoma, sans-serif;

&.active{
    color: rgba(80, 51, 130, 1);
    border-style: none none solid none;
    border-width: 2px;
    border-color: rgba(255, 0, 157, .7);
    

}
&:hover {
    border-style: none none solid none;
    border-width: 2px;
    border-color: rgba(80, 51, 130, 1);
}
`

export const NavMenuL = styled.div`
display: flex;
align-item: center;
margin-left .2rem;
`
export const NavMenuR = styled.div`
display: flex;
align-item: center;
margin-right .2rem;
`

export const NavBtn = styled.nav`
display: flex;
align-items: center;
margin-right: 24px;

`

export const NavBtnLink = styled(Link)`
border-radius: 4px;
background: #256ce1;
padding: 10px 22px;
color: #fff;
border: none;
outline: none;
cursor: pointer;
transition: all 0.2s ease-in-out;
text-dectoration: none;
font-family: Verdana, Geneva, Tahoma, sans-serif;


&hover {
    transition: all 0.2s ease-in-out;
    background: #fff
}
`