package main

import (
	"fmt"
	"math/rand"
	"time"
)

// Player represents a game player
type Player struct {
	ID       int
	Name     string
	Score    int
	Health   int
	Level    int
	Position Position
}

// Position represents a player's position in the game world
type Position struct {
	X, Y int
}

// Game represents the game state
type Game struct {
	Players    []Player
	GameActive bool
	Round      int
	WorldSize  int
}

// NewGame creates a new game instance
func NewGame(worldSize int) *Game {
	return &Game{
		Players:    make([]Player, 0),
		GameActive: false,
		Round:      0,
		WorldSize:  worldSize,
	}
}

// AddPlayer adds a new player to the game
func (g *Game) AddPlayer(name string) {
	player := Player{
		ID:     len(g.Players) + 1,
		Name:   name,
		Score:  0,
		Health: 100,
		Level:  1,
		Position: Position{
			X: rand.Intn(g.WorldSize),
			Y: rand.Intn(g.WorldSize),
		},
	}
	g.Players = append(g.Players, player)
	fmt.Printf("Player %s joined the game at position (%d, %d)\n",
		player.Name, player.Position.X, player.Position.Y)
}

// StartGame begins the game simulation
func (g *Game) StartGame() {
	if len(g.Players) < 2 {
		fmt.Println("Need at least 2 players to start the game!")
		return
	}

	g.GameActive = true
	g.Round = 1
	fmt.Printf("\n🎮 Game Started with %d players!\n", len(g.Players))
	fmt.Println("=" + string(make([]byte, 40)) + "=")
}

// MovePlayer moves a player to a new random position
func (g *Game) MovePlayer(playerID int) {
	if playerID > len(g.Players) || playerID < 1 {
		return
	}

	player := &g.Players[playerID-1]
	oldPos := player.Position

	// Random movement within bounds
	deltaX := rand.Intn(3) - 1 // -1, 0, or 1
	deltaY := rand.Intn(3) - 1

	newX := player.Position.X + deltaX
	newY := player.Position.Y + deltaY

	// Keep within world bounds
	if newX >= 0 && newX < g.WorldSize {
		player.Position.X = newX
	}
	if newY >= 0 && newY < g.WorldSize {
		player.Position.Y = newY
	}

	fmt.Printf("%s moved from (%d,%d) to (%d,%d)\n",
		player.Name, oldPos.X, oldPos.Y, player.Position.X, player.Position.Y)
}

// SimulateBattle simulates a battle between two nearby players
func (g *Game) SimulateBattle(player1ID, player2ID int) {
	if player1ID > len(g.Players) || player2ID > len(g.Players) ||
		player1ID < 1 || player2ID < 1 || player1ID == player2ID {
		return
	}

	p1 := &g.Players[player1ID-1]
	p2 := &g.Players[player2ID-1]

	// Check if players are close enough to battle (distance <= 2)
	distance := abs(p1.Position.X-p2.Position.X) + abs(p1.Position.Y-p2.Position.Y)
	if distance > 2 {
		return
	}

	fmt.Printf("\n⚔️  Battle between %s and %s!\n", p1.Name, p2.Name)

	// Simple battle simulation
	p1Damage := rand.Intn(20) + 10 + p1.Level*5
	p2Damage := rand.Intn(20) + 10 + p2.Level*5

	p1.Health -= p2Damage
	p2.Health -= p1Damage

	fmt.Printf("%s deals %d damage to %s (Health: %d)\n",
		p1.Name, p1Damage, p2.Name, p2.Health)
	fmt.Printf("%s deals %d damage to %s (Health: %d)\n",
		p2.Name, p2Damage, p1.Name, p1.Health)

	// Determine winner and award points
	if p1.Health <= 0 && p2.Health <= 0 {
		fmt.Println("💀 Both players defeated!")
		p1.Health = 50 // Respawn with half health
		p2.Health = 50
	} else if p1.Health <= 0 {
		fmt.Printf("🏆 %s wins the battle!\n", p2.Name)
		p2.Score += 100
		p1.Health = 50 // Respawn
		g.checkLevelUp(p2)
	} else if p2.Health <= 0 {
		fmt.Printf("🏆 %s wins the battle!\n", p1.Name)
		p1.Score += 100
		p2.Health = 50 // Respawn
		g.checkLevelUp(p1)
	}
}

// checkLevelUp checks if a player should level up
func (g *Game) checkLevelUp(player *Player) {
	requiredScore := player.Level * 200
	if player.Score >= requiredScore {
		player.Level++
		player.Health += 20 // Bonus health on level up
		fmt.Printf("🎉 %s leveled up to Level %d!\n", player.Name, player.Level)
	}
}

// SimulateRound simulates one round of the game
func (g *Game) SimulateRound() {
	if !g.GameActive {
		return
	}

	fmt.Printf("\n--- Round %d ---\n", g.Round)

	// Move all players
	for i := range g.Players {
		g.MovePlayer(i + 1)
	}

	// Random events
	eventChance := rand.Intn(100)
	if eventChance < 30 {
		g.randomEvent()
	}

	// Check for battles between nearby players
	for i := 0; i < len(g.Players); i++ {
		for j := i + 1; j < len(g.Players); j++ {
			if rand.Intn(100) < 40 { // 40% chance of battle if close
				g.SimulateBattle(i+1, j+1)
			}
		}
	}

	g.Round++
}

// randomEvent triggers a random game event
func (g *Game) randomEvent() {
	events := []string{
		"💰 Treasure found! All players gain 50 points!",
		"🌟 Power-up spawned! Random player gains health!",
		"⚡ Lightning storm! All players lose 10 health!",
		"🍎 Health potions discovered! All players gain 20 health!",
	}

	event := events[rand.Intn(len(events))]
	fmt.Printf("🎲 Random Event: %s\n", event)

	switch event {
	case events[0]: // Treasure
		for i := range g.Players {
			g.Players[i].Score += 50
		}
	case events[1]: // Power-up
		if len(g.Players) > 0 {
			lucky := rand.Intn(len(g.Players))
			g.Players[lucky].Health += 30
			fmt.Printf("   %s received the power-up!\n", g.Players[lucky].Name)
		}
	case events[2]: // Lightning
		for i := range g.Players {
			g.Players[i].Health -= 10
			if g.Players[i].Health < 10 {
				g.Players[i].Health = 10
			}
		}
	case events[3]: // Health potions
		for i := range g.Players {
			g.Players[i].Health += 20
			if g.Players[i].Health > 100 {
				g.Players[i].Health = 100
			}
		}
	}
}

// PrintGameState displays current game state
func (g *Game) PrintGameState() {
	fmt.Println("\n📊 Current Game State:")
	fmt.Println("=" + string(make([]byte, 50)) + "=")

	for _, player := range g.Players {
		fmt.Printf("Player: %-10s | Score: %-4d | Health: %-3d | Level: %d | Pos: (%d,%d)\n",
			player.Name, player.Score, player.Health, player.Level,
			player.Position.X, player.Position.Y)
	}
	fmt.Println()
}

// GetWinner returns the player with the highest score
func (g *Game) GetWinner() *Player {
	if len(g.Players) == 0 {
		return nil
	}

	winner := &g.Players[0]
	for i := range g.Players {
		if g.Players[i].Score > winner.Score {
			winner = &g.Players[i]
		}
	}
	return winner
}

// EndGame ends the game and declares winner
func (g *Game) EndGame() {
	g.GameActive = false
	winner := g.GetWinner()

	fmt.Println("\n🏁 Game Over!")
	fmt.Println("=" + string(make([]byte, 40)) + "=")

	if winner != nil {
		fmt.Printf("🥇 Winner: %s with %d points!\n", winner.Name, winner.Score)
	}

	fmt.Println("\nFinal Standings:")
	// Sort players by score (simple bubble sort for demo)
	players := make([]Player, len(g.Players))
	copy(players, g.Players)

	for i := 0; i < len(players); i++ {
		for j := 0; j < len(players)-1-i; j++ {
			if players[j].Score < players[j+1].Score {
				players[j], players[j+1] = players[j+1], players[j]
			}
		}
	}

	for i, player := range players {
		fmt.Printf("%d. %s - %d points (Level %d)\n",
			i+1, player.Name, player.Score, player.Level)
	}
}

// abs returns absolute value of an integer
func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// Main function to run the game simulation
func main() {
	rand.Seed(time.Now().UnixNano())

	fmt.Println("🎮 Welcome to the Discord Bot Game Simulation!")
	fmt.Println("=" + string(make([]byte, 45)) + "=")

	// Create new game
	game := NewGame(10) // 10x10 world

	// Add players
	playerNames := []string{"Alice", "Bob", "Charlie", "Diana", "Eve"}
	for _, name := range playerNames {
		game.AddPlayer(name)
	}

	// Start the game
	game.StartGame()

	// Simulate 10 rounds
	for round := 1; round <= 10; round++ {
		game.SimulateRound()
		game.PrintGameState()

		// Add some delay for readability
		time.Sleep(500 * time.Millisecond)
	}

	// End the game
	game.EndGame()
}
