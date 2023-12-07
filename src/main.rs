pub mod sites;
pub mod misc;

use sites::m4l::get_every;

#[tokio::main]
async fn main() {
    get_every().await;
}
