import "./About.css"
import LDA from "../Images/LDAModel.png"
import precomputed from "../Images/precomputed.png"
import runtime from "../Images/runtimeProcess.png"



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
            <p>One key takeaway from the project was designing a fully functioning and comprehensive system. For our system, we start with the user query. The user inputs some block of text, and we tokenize the text, and then feed that into the models. We have a <a href="https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation"> trained LDA model</a> that splits the text into 10 topics, we have index matching which is pure tf, no idf, and we have success rate, which is the winning percentage for a given opening. After LDA, index matching and success rate are calculated and weighted, they are averaged, and based off of the scores, the top 5 matches for openings are returned. The returned openings are then summarized, and returned to the user in order. We discovered that in order to maximize the potential of this application, we would be best off precomputing most of the work, so at runtime, the user doesn't have to wait for long. We precomputed the LDA model, the index matching, the success rate, and most of the summary work.   </p>
            <img src={precomputed} alt="precomputed" />
            <img src={runtime} alt="runtime" />

            <br></br>
            <br></br>
            <br></br>

            <p>Another key takeaway from the project was how to interact with and train an LDA model, and the intricacies that come with that. This is a brief breakdown of the LDA model we trained. To start, we feed a tokenized description to the model. This could be either the user's query, or a description of an opening. The model then breaks the text down into chunks of no greater than 1024 tokens (The exact number is specific to the model used). It does this “i” times, with “i” roughly being the number of words in the description divided by t, which is 1024 for this model. Each of these chunks then gives a summary between 10 to 50 words. (The length of the summaries can be changed). The summaries are all concatenated. If the length of the concatenated summaries is greater than t (1024), then the process is done again, with the concatenated summary being re-split into “i” chunks, and each chunk being summarized once again. The process repeats until the concatenated summary is less than 1024 tokens. Once this happens, the summary goes through the model one final time before it is done. This is to get a summary of all the concatenated summaries, as one final summary.</p>
            <img src={LDA} alt="LDA" />



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