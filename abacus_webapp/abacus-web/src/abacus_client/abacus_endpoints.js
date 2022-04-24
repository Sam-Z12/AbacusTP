
export async function fetchHome(){
    const endpoint = 'http://localhost:5000';
    return await (await fetch(endpoint)).json();
}

