use bytes::Bytes;
use std::io::Write;
use std::{error::Error, fs::File};

use camino::Utf8Path;
use reqwest::Client;

#[tokio::main]
async fn main() {
    let client = Client::new();
    let url = "https://scans-hot.leanbox.us/manga/Chainsaw-Man/0150-001.png";
    let _ = match get_page(client, url).await {
        Ok(_) => {}
        Err(err) => panic!("Can't Get page {} {:?}", url, err),
    };
}

async fn get_page(client: Client, url: &str) -> Result<(), Box<dyn Error>> {
    let mut res = client.get(url).send().await?;
    let file_content = res.bytes().await?;

    let path = Utf8Path::new("./file.png");
    write_file(path, file_content)?;
    Ok(())
}

fn write_file(file_path: &Utf8Path, file_content: Bytes) -> Result<(), Box<dyn Error>> {
    let mut file = File::create(file_path)?;
    file.write_all(file_content.as_ref())?;
    Ok(())
}