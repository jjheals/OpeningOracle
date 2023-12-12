import "./About.css"

function About() {
    return (
        <div>
            <h2>About Our Project</h2>
            <p className="center">We are a team of three students from <a href="https://www.wpi.edu/">Worcester Polytechnic Institute (WPI)</a> in Massachusetts</p>
            <p className="center">Our project, OpeningOracle, is the final project for CS 547: Information Retrieval under Prof. Kyumin Lee</p>
            <br />
            <p>
                OpeningOracle is a solution for chess players to find statistically successful openings to play based on their own description of how they like to play. Both experienced and inexperienced players can benefit from this; experienced players who know their preferred playstyle can find new openings they may not have known about before, and new players who are not yet sure how they like to play can find openings based on different playstyles.
                <br />
                <br />
                The primary goal of OpeningOracle, and what sets it apart from other applications, is that users can arbitrarily describe their playstyle. There are current applications that provide opening recommendations based on pre-set parameters, like the user's self-reported skill level, some keywords to choose from, and/or a color to play with. At the time of writing, we did not come across any solutions that allow the user to arbitrarily define their own playstyle, and very few that operate independently of the user's reported playstyle.
            </p>

            <h2>Big Questions</h2>
            <p className="center">Can an algorithm accurately recommend chess openings based on arbitrary text input?</p>
            <p className="center">How can we assess accuracy of recommended openings?</p>

            <h2>Key Takeaways</h2>

            <h2>External Resources and Data Used</h2>
            <p>Our <a className="link" href="https://github.com/jjheals/OpeningOracle/">Github</a> and <a className="link" href="https://github.com/jjheals/OpeningOracle/blob/main/README.md">README</a>, with instructions on running our code and installing dependencies.</p>
            <p>We used <a className="link" href="https://www.wikipedia.org/">Wikipedia</a> to scrape descriptions of chess openings.</p>

            <p>We scraped <a className="link" href="https://www.chess.com/home">Chess.com</a> as a starting point to get opening ECO codes, names, and descriptions.</p>
            <p>We utilized a <a className="link" href="https://www.kaggle.com/datasets/datasnaek/chess">Lichess dataset from Kaggle</a> as one source of opening success rates, and to get the ECOs and names of openings that were not on Chess.com.</p>
            <p>We also utilized a <a className="link" href="https://www.kaggle.com/datasets/arashnic/chess-opening-dataset">High Elo Chess Games Dataset from Kaggle</a> to get the color for each opening (i.e. which color plays, responds to, or initiates an opening), and as a second source of opening success rates.</p>
        </div>
    );
}

export default About;