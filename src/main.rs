pub mod sites;
pub mod misc;

use misc::prompt_user;
use sites::m4l::get_multiple_chapters;

#[tokio::main]
async fn main() {
    let ans = prompt_user();
    get_multiple_chapters(ans).await
}
