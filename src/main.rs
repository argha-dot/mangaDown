pub mod sites;
pub mod utils;

use reqwest::Client;
use sites::m4l::download_chapter;

#[tokio::main]
async fn main() {
    let client = Client::new();
    download_chapter(
        "https://scans-hot.leanbox.us/manga/Chainsaw-Man/",
        "Chainsaw Man",
        150.0,
        &client,
    )
    .await;
    // download_chapter(
    //     "https://scans-hot.leanbox.us/manga/Oshi-no-Ko/0125.8-001.png",
    //     "Oshi no Ko",
    //     125.8,
    //     &client,
    // )
    // .await;
}
